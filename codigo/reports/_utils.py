"""
Funciones de utilidad internas para la aplicación de reportes.
"""
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Report
from .forms import ReportForm, ReportFilterForm, ReportResponseForm
from .constants import (
    REPORT_LIST_NAME, REPORT_DETAIL_NAME, CREATE_REPORT_NAME,
    UPDATE_REPORT_NAME, DELETE_REPORT_NAME, MARK_READ_NAME, MARK_UNREAD_NAME,
    get_url_full, REPORTS_PER_PAGE, USER_ID_PARAM, RIDE_ID_PARAM, PAYMENT_ID_PARAM,
    REPORT_CREATED_SUCCESS, REPORT_UPDATED_SUCCESS, REPORT_DELETED_SUCCESS, 
    RESPONSE_SENT_SUCCESS, NO_PERMISSION_ERROR, NO_VIEW_PERMISSION_ERROR,
    REPORT_ALREADY_RESPONDED_ERROR, NO_MARK_PERMISSION_ERROR,
    REPORT_MARKED_READ, REPORT_MARKED_UNREAD
)

def get_report_or_404(pk):
    """
    Obtiene un reporte o devuelve un 404.
    """
    return get_object_or_404(Report, pk=pk)

def check_report_view_permission(request, report):
    """
    Verifica que el usuario tenga permiso para ver el reporte.
    """
    if not (request.user.is_staff or request.user == report.user):
        return HttpResponseForbidden(NO_VIEW_PERMISSION_ERROR)
    return None

def check_report_edit_permission(request, report):
    """
    Verifica que el usuario tenga permiso para editar el reporte.
    """
    # Solo el creador o un admin pueden editar
    if not (request.user.is_staff or request.user == report.user):
        return HttpResponseForbidden(NO_PERMISSION_ERROR)
    
    # No se puede editar si ya tiene respuesta
    if report.response and not request.user.is_staff:
        messages.warning(request, REPORT_ALREADY_RESPONDED_ERROR)
        return redirect(get_url_full(REPORT_DETAIL_NAME), pk=report.pk)
    
    return None

def check_admin_permission(request):
    """
    Verifica que el usuario sea un administrador.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden(NO_MARK_PERMISSION_ERROR)
    return None

def filter_reports(request, reports):
    """
    Aplica filtros a los reportes según los parámetros GET.
    """
    filter_form = ReportFilterForm(request.GET)
    
    if filter_form.is_valid():
        # Filtrar por tipo
        if report_type := filter_form.cleaned_data.get('report_type'):
            reports = reports.filter(report_type=report_type)
        
        # Filtrar por importancia
        if importance := filter_form.cleaned_data.get('importance'):
            reports = reports.filter(importance=importance)
        
        # Filtrar por leídos/no leídos
        if filter_form.cleaned_data.get('read'):
            reports = reports.filter(read=False)
        
        # Búsqueda de texto
        if search := filter_form.cleaned_data.get('search'):
            reports = reports.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
    
    return reports, filter_form

def paginate_reports(request, reports):
    """
    Pagina los reportes.
    """
    paginator = Paginator(reports, REPORTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def prepare_report_context(report, user):
    """
    Prepara el contexto para la vista de detalle de un reporte.
    """
    context = {
        'report': report,
        'is_admin': user.is_staff,
    }
    
    if user.is_staff:
        context['response_form'] = ReportResponseForm(instance=report)
    
    return context

def prepare_report_list_context(page_obj, filter_form, user):
    """
    Prepara el contexto para la vista de lista de reportes.
    """
    return {
        'reports': page_obj,
        'filter_form': filter_form,
        'page_obj': page_obj,
        'is_paginated': True,
        'paginator': page_obj.paginator,
        'is_admin': user.is_staff
    }

def handle_report_response(request, report):
    """
    Maneja la respuesta a un reporte.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden(NO_PERMISSION_ERROR)
    
    response_form = ReportResponseForm(request.POST, instance=report)
    if response_form.is_valid():
        report_response = response_form.save(commit=False)
        report_response.response_by = request.user
        report_response.response_at = timezone.now()
        report_response.save()
        messages.success(request, RESPONSE_SENT_SUCCESS)
        return redirect(get_url_full(REPORT_DETAIL_NAME), pk=report.pk)
    
    return None

def get_related_objects(request):
    """
    Obtiene objetos relacionados para un reporte (usuario, viaje, pago).
    """
    from django.contrib.auth.models import User
    from rides.models import Ride
    from payments.models import Payment
    
    reported_user = None
    ride = None
    payment = None
    initial_data = {}
    
    user_id = request.GET.get(USER_ID_PARAM)
    ride_id = request.GET.get(RIDE_ID_PARAM)
    payment_id = request.GET.get(PAYMENT_ID_PARAM)
    
    if user_id:
        reported_user = get_object_or_404(User, pk=user_id)
        initial_data['report_type'] = Report.USER
        initial_data['title'] = f'Reporte sobre usuario: {reported_user.username}'
    elif ride_id:
        ride = get_object_or_404(Ride, pk=ride_id)
        initial_data['report_type'] = Report.RIDE
        initial_data['title'] = f'Reporte sobre viaje: {ride.origin} a {ride.destination}'
    elif payment_id:
        payment = get_object_or_404(Payment, pk=payment_id)
        initial_data['report_type'] = Report.PAYMENT
        initial_data['title'] = f'Reporte sobre pago de {payment.amount}€ a {payment.recipient.username}'
    
    return reported_user, ride, payment, initial_data

def prepare_create_report_context(form, reported_user, ride, payment):
    """
    Prepara el contexto para la vista de creación de un reporte.
    """
    return {
        'form': form,
        'reported_user': reported_user,
        'ride': ride,
        'payment': payment,
    }
