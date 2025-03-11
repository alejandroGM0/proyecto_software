from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment
from rides.models import Ride
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from .forms import PaymentForm 

@login_required
def payment_list(request):
    """Vista para mostrar todos los pagos del usuario actual"""
    # Mostrar pagos realizados y recibidos por el usuario
    payments_made = Payment.objects.filter(payer=request.user).order_by('-created_at')
    payments_received = Payment.objects.filter(recipient=request.user).order_by('-created_at')
    
    return render(request, 'payments/payment_list.html', {
        'payments_made': payments_made,
        'payments_received': payments_received,
    })

@login_required
def payment_detail(request, payment_id):
    """Vista para ver detalles de un pago específico"""
    # Asegurarse de que el usuario solo pueda ver sus propios pagos
    payment = get_object_or_404(
        Payment, 
        id=payment_id, 
        pk__isnull=False,  # This condition is always true, used as a placeholder
        user_filter=Q(payer=request.user) | Q(recipient=request.user)
    )
    
    return render(request, 'payments/payment_detail.html', {
        'payment': payment,
    })

@login_required
def create_payment(request, ride_id=None):
    """Vista para crear un nuevo pago"""
    ride = None
    if ride_id:
        ride = get_object_or_404(Ride, id=ride_id)
        # Verificar que el usuario está reservando este viaje
        if request.user not in ride.passengers.all() and request.user != ride.driver:
            messages.error(request, 'No tienes permiso para realizar este pago.')
            return redirect('rides:ride_list')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payer = request.user
            
            # Si el pago es para un viaje específico
            if ride:
                payment.ride = ride
                payment.recipient = ride.driver
                payment.amount = ride.price
            
            payment.save()
            messages.success(request, '¡Pago realizado con éxito!')
            return redirect('payments:payment_detail', payment_id=payment.id)
    else:
        initial_data = {}
        if ride:
            initial_data = {
                'ride': ride,
                'recipient': ride.driver,
                'amount': ride.price
            }
        form = PaymentForm(initial=initial_data)
    
    return render(request, 'payments/payment_form.html', {
        'form': form,
        'ride': ride
    })

@login_required
def cancel_payment(request, payment_id):
    """Vista para cancelar un pago pendiente"""
    payment = get_object_or_404(Payment, id=payment_id, payer=request.user, status=Payment.PENDING)
    
    if request.method == 'POST':
        payment.status = Payment.FAILED
        payment.save()
        messages.success(request, 'Pago cancelado correctamente.')
        return redirect('payments:payment_list')
    
    return render(request, 'payments/cancel_payment.html', {
        'payment': payment
    })

@login_required
def refund_payment(request, payment_id):
    """Vista para reembolsar un pago (solo para el receptor)"""
    payment = get_object_or_404(Payment, id=payment_id, recipient=request.user, status=Payment.COMPLETED)
    
    if request.method == 'POST':
        payment.status = Payment.REFUNDED
        payment.save()
        messages.success(request, 'Reembolso procesado correctamente.')
        return redirect('payments:payment_list')
    
    return render(request, 'payments/refund_payment.html', {
        'payment': payment
    })

@login_required
def ride_payment(request, ride_id):
    """Vista específica para realizar el pago de un viaje"""
    ride = get_object_or_404(Ride, id=ride_id)
    
    # Verificar que el usuario es pasajero del viaje
    if request.user not in ride.passengers.all():
        messages.error(request, 'Debes reservar este viaje antes de poder pagarlo.')
        return redirect('rides:ride_detail', ride_id=ride.id)
    
    # Verificar si ya existe un pago para este usuario y viaje
    existing_payment = Payment.objects.filter(
        payer=request.user,
        ride=ride,
        status__in=[Payment.PENDING, Payment.COMPLETED]
    ).first()
    
    if existing_payment:
        messages.info(request, 'Ya tienes un pago registrado para este viaje.')
        return redirect('payments:payment_detail', payment_id=existing_payment.id)
    
    # Redireccionar a la vista de creación de pago con el viaje preseleccionado
    return redirect('payments:create_payment', ride_id=ride.id)

@login_required
def payment_history(request):
    """Vista para mostrar el historial completo de pagos del usuario"""
    payments = Payment.objects.filter(
        Q(payer=request.user) | Q(recipient=request.user)
    ).order_by('-created_at')
    
    # Filtrar por estado si se especifica en la URL
    status_filter = request.GET.get('status')
    if status_filter and hasattr(Payment, status_filter.upper()):
        payments = payments.filter(status=getattr(Payment, status_filter.upper()))
    
    return render(request, 'payments/payment_history.html', {
        'payments': payments,
        'status_filter': status_filter,
    })

