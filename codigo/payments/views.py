from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect

from rides.models import Ride
from .models import Payment
from .forms import PaymentInitForm, PaymentForm
from . import _utils
from .constants import (
    PAYMENT_STATUS_PENDING, PAYMENT_STATUS_COMPLETED, 
    PAYMENT_STATUS_FAILED, PAYMENT_STATUS_REFUNDED,
    PAYMENT_STATUS_CANCELLED, PAYMENT_METHOD_STRIPE,
    ERROR_OWN_RIDE_PAYMENT, ERROR_PERMISSION_DENIED,
    ERROR_ALREADY_PAID, ERROR_PAYMENT_PENDING,
    ERROR_PAYMENT_PROCESSING, SUCCESS_PAYMENT_COMPLETED,
    SUCCESS_PAYMENT_REFUNDED, SUCCESS_PAYMENT_CANCELLED,
    INFO_PAYMENT_CANCELLED, INFO_PAYMENT_VERIFYING
)

@login_required
def payment_list(request):
    """
    Vista para mostrar los pagos del usuario (realizados y recibidos)
    """
    payments_made = Payment.objects.filter(payer=request.user).order_by('-created_at')
    payments_received = Payment.objects.filter(recipient=request.user).order_by('-created_at')
    
    context = {
        'payments_made': payments_made,
        'payments_received': payments_received
    }
    
    return render(request, 'payments/payment_list.html', context)

@login_required
def payment_detail(request, pk):
    """
    Vista para ver detalles de un pago específico
    """
    payment = get_object_or_404(Payment, pk=pk)
    
    if not _utils.validate_payment_access(payment, request.user):
        messages.error(request, ERROR_PERMISSION_DENIED)
        return redirect('payments:payment_list')
    
    context = {
        'payment': payment,
        'is_admin': request.user.is_staff or request.user.is_superuser  # Flag para ver si es admin
    }
    
    return render(request, 'payments/payment_detail.html', context)

@login_required
def payment_history(request):
    """
    Vista para el historial completo de pagos
    """
    from django.db.models import Q
    
    payments = Payment.objects.filter(
        Q(payer=request.user) | Q(recipient=request.user)
    ).order_by('-created_at')
    
    status_filter = request.GET.get('status', '').upper()
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    context = {
        'payments': payments,
        'status_filter': request.GET.get('status', '').lower()
    }
    
    return render(request, 'payments/payment_history.html', context)

@login_required
def create_payment(request, ride_id):
    """
    Vista para iniciar el proceso de pago de un viaje
    """
    ride = get_object_or_404(Ride, pk=ride_id)
    
    if ride.driver == request.user:
        messages.error(request, ERROR_OWN_RIDE_PAYMENT)
        return redirect('rides:ride_detail', ride_id=ride_id)
    
    if ride.seats_available <= 0:
        messages.error(request, "Este viaje está completo, no hay asientos disponibles.")
        return redirect('rides:ride_detail', ride_id=ride_id)
    
    existing_payment = Payment.objects.filter(
        payer=request.user,
        ride=ride,
        status__in=[PAYMENT_STATUS_PENDING, PAYMENT_STATUS_COMPLETED]
    ).first()
    
    if existing_payment:
        if existing_payment.status == PAYMENT_STATUS_COMPLETED:
            messages.info(request, ERROR_ALREADY_PAID)
            return redirect('rides:ride_detail', ride_id=ride_id)
        else:
            messages.info(request, ERROR_PAYMENT_PENDING)
            return redirect('rides:ride_detail', ride_id=ride_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = Payment(
                payer=request.user,
                recipient=ride.driver,
                amount=ride.price,
                ride=ride,
                status=PAYMENT_STATUS_PENDING
            )
            payment.save()
            
            checkout_url = _utils.create_checkout_session(payment, request)
            
            if checkout_url:
                return redirect(checkout_url)
            else:
                messages.error(request, ERROR_PAYMENT_PROCESSING)
                payment.status = PAYMENT_STATUS_FAILED
                payment.save()
                return redirect('rides:ride_detail', ride_id=ride_id)
    else:
        form = PaymentForm()
    
    return render(request, 'payments/create_payment.html', {
        'form': form,
        'ride': ride
    })

@login_required
def payment_success(request, pk):
    """
    Vista para manejar el retorno exitoso de Stripe
    """
    payment = get_object_or_404(Payment, pk=pk)
    session_id = request.GET.get('session_id')
    
    if session_id:
        status = _utils.get_payment_status(session_id)
        
        if status == 'succeeded':
            payment.status = PAYMENT_STATUS_COMPLETED
            payment.save()
            
            if payment.ride:
                from rides.public import add_passenger_to_ride
                if add_passenger_to_ride(payment.payer, payment.ride):
                    messages.success(request, "¡Has reservado tu asiento con éxito!")
                else:
                    messages.warning(request, "El pago fue exitoso, pero no se pudo reservar el asiento. Por favor, contacta con soporte.")
            
            messages.success(request, SUCCESS_PAYMENT_COMPLETED)
        else:
            messages.warning(request, INFO_PAYMENT_VERIFYING)
    
    return redirect('payments:payment_detail', pk=payment.pk)

@login_required
def payment_cancel(request, pk):
    """
    Vista para manejar la cancelación del pago en Stripe
    """
    payment = get_object_or_404(Payment, pk=pk)
    
    # Verificar que el usuario tiene permiso para cancelar el pago
    if payment.payer != request.user:
        messages.error(request, ERROR_PERMISSION_DENIED)
        return redirect('payments:payment_list')
    
    if payment.status == PAYMENT_STATUS_PENDING:
        payment.status = PAYMENT_STATUS_CANCELLED
        payment.save()
        messages.info(request, INFO_PAYMENT_CANCELLED)
    
    return redirect('payments:payment_list')

@login_required
def refund_payment(request, pk):
    """
    Vista para reembolsar un pago
    """
    payment = get_object_or_404(Payment, pk=pk)
    
    has_permission, error_msg = _utils.validate_refund_permission(payment, request.user)
    if not has_permission:
        messages.error(request, error_msg)
        return redirect('payments:payment_detail', pk=payment.pk)
    
    if request.method == 'POST':
        success, result = _utils.process_refund(payment)
        
        if success:
            payment.status = PAYMENT_STATUS_REFUNDED
            payment.stripe_refund_id = result
            payment.save()
            messages.success(request, SUCCESS_PAYMENT_REFUNDED)
            return redirect('payments:payment_detail', pk=payment.pk)
        else:
            messages.error(request, f"Error al procesar el reembolso: {result}")
    
    context = {
        'payment': payment
    }
    
    return render(request, 'payments/refund_payment.html', context)

@login_required
@require_POST
def cancel_payment(request, pk):
    """
    Vista para cancelar un pago pendiente
    """
    payment = get_object_or_404(Payment, pk=pk)
    
    has_permission, error_msg = _utils.validate_cancel_permission(payment, request.user)
    if not has_permission:
        messages.error(request, error_msg)
        return redirect('payments:payment_detail', pk=payment.pk)
    
    payment.status = PAYMENT_STATUS_CANCELLED
    payment.save()
    
    messages.success(request, SUCCESS_PAYMENT_CANCELLED)
    return redirect('payments:payment_list')
