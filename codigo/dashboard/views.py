# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
Vistas para la aplicación de dashboard
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from rides.public import get_rides_published_in_period, get_recently_published_rides

from ._utils import (
    get_dashboard_data, get_rides_data, get_messages_data, 
    get_reports_data, get_users_data, get_payments_data,
    serialize_dashboard_data, get_system_status, 
    get_recent_activities, get_ride_activities, 
    get_ride_management_context, get_user_management_context,
    get_date_range_for_period, get_chat_management_context
)

from .constants import (
    TEMPLATE_DASHBOARD, TEMPLATE_TRIP_STATS,
    TEMPLATE_MSG_STATS, TEMPLATE_REPORT_STATS,
    TEMPLATE_USER_STATS, TEMPLATE_REPORT_DETAIL,
    TEMPLATE_RIDE_MANAGEMENT, TEMPLATE_USER_MANAGEMENT,
    CONTEXT_TRIP_DATA, CONTEXT_MSG_DATA, CONTEXT_REPORT_DATA,
    CONTEXT_USER_DATA, CONTEXT_PAYMENT_DATA, CONTEXT_TIME_PERIOD,
    DEFAULT_PERIOD, TEMPLATE_CHAT_MANAGEMENT
)

from accounts.public import get_active_users, delete_user
from reports.public import get_report_by_id, update_report_status
from rides.public import delete_ride, get_active_rides_today, get_seats_available
from payments.public import get_recent_payments

def is_admin(user):
    """
    Verifica si el usuario es administrador
    """
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """
    Vista principal del dashboard
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    context = get_dashboard_data(period=period, active_section='main')
    
    context['trip_data_json'] = serialize_dashboard_data(context['trip_data'])
    context['msg_data_json'] = serialize_dashboard_data(context['msg_data'])
    context['report_data_json'] = serialize_dashboard_data(context['report_data'])
    context['user_data_json'] = serialize_dashboard_data(context['user_data'])
    context['payment_data_json'] = serialize_dashboard_data(context['payment_data'])
    
    context['active_users'] = get_active_users(minutes=30)
    context['active_rides_today'] = get_active_rides_today()
    context['total_seats'] = get_seats_available()
    
    
    context['recent_activities'] = get_recent_activities(include_rides=False)
    context['ride_activities'] = get_ride_activities()
    
    context['recently_published_rides'] = get_recently_published_rides(limit=3)
    
    today = timezone.now().date()
    context['recent_payments'] = get_recent_payments(days=7, limit=5)
    
    
    context['system_status'] = get_system_status()
    
    return render(request, TEMPLATE_DASHBOARD, context)

@login_required
@user_passes_test(is_admin)
def ride_management(request):
    """
    Vista para la gestión de viajes
    """
    
    if request.method == 'POST' and 'delete_ride' in request.POST:
        ride_id = request.POST.get('ride_id')
        if delete_ride(ride_id):
            messages.success(request, 'Viaje eliminado con éxito.')
    
    
    context = get_ride_management_context(request)
    context['active_section'] = 'ride_management'
    
    return render(request, TEMPLATE_RIDE_MANAGEMENT, context)

@login_required
@user_passes_test(is_admin)
def user_management(request):
    """
    Vista para la gestión de usuarios
    """
    
    if request.method == 'POST' and 'delete_user' in request.POST:
        user_id = request.POST.get('user_id')
        if delete_user(user_id):
            messages.success(request, 'Usuario eliminado con éxito.')
    
    context = get_user_management_context(request)
    context['active_section'] = 'user_management'
    
    return render(request, TEMPLATE_USER_MANAGEMENT, context)

@login_required
@user_passes_test(is_admin)
def chat_management(request):
    """
    Vista para la gestión de chats
    """
    
    if request.method == 'POST' and 'delete_chat' in request.POST:
        chat_id = request.POST.get('chat_id')
        from chat.public import delete_chat
        if delete_chat(chat_id):
            messages.success(request, 'Chat eliminado con éxito.')
    
    context = get_chat_management_context(request)
    context['active_section'] = 'chat_management'
    
    return render(request, TEMPLATE_CHAT_MANAGEMENT, context)

@login_required
@user_passes_test(is_admin)
def dashboard_data_api(request):
    """
    API para obtener datos del dashboard de forma asíncrona
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    trip_data = get_rides_data(period)
    msg_data = get_messages_data(period)
    report_data = get_reports_data(period)
    user_data = get_users_data(period)
    payment_data = get_payments_data(period)
    
    data = {
        'trip_data': trip_data,
        'msg_data': msg_data,
        'report_data': report_data,
        'user_data': user_data,
        'payment_data': payment_data
    }
    
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def trip_stats(request):
    """
    Vista de estadísticas de viajes
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    trip_data = get_rides_data(period)
    
    start_date, end_date, period_text = get_date_range_for_period(period)
    trip_data['period_text'] = period_text
    
    trip_data['published_in_period'] = get_rides_published_in_period(start_date, end_date)
    
    context = {
        CONTEXT_TRIP_DATA: trip_data,
        CONTEXT_TIME_PERIOD: period,
        'active_section': 'trips',
        'trip_data_json': serialize_dashboard_data(trip_data)
    }
    
    return render(request, TEMPLATE_TRIP_STATS, context)

@login_required
@user_passes_test(is_admin)
def message_stats(request):
    """
    Vista de estadísticas de mensajes
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    msg_data = get_messages_data(period)
    
    
    start_date, end_date, period_text = get_date_range_for_period(period)
    msg_data['period_text'] = period_text
    
    context = {
        CONTEXT_MSG_DATA: msg_data,
        CONTEXT_TIME_PERIOD: period,
        'active_section': 'messages',
        'msg_data_json': serialize_dashboard_data(msg_data)
    }
    
    return render(request, TEMPLATE_MSG_STATS, context)

@login_required
@user_passes_test(is_admin)
def report_stats(request):
    """
    Vista de estadísticas de reportes
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    report_data = get_reports_data(period)
    
    
    start_date, end_date, period_text = get_date_range_for_period(period)
    report_data['period_text'] = period_text
    
    context = {
        CONTEXT_REPORT_DATA: report_data,
        CONTEXT_TIME_PERIOD: period,
        'active_section': 'reports',
        'report_data_json': serialize_dashboard_data(report_data)
    }
    
    return render(request, TEMPLATE_REPORT_STATS, context)

@login_required
@user_passes_test(is_admin)
def user_stats(request):
    """
    Vista de estadísticas de usuarios
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    user_data = get_users_data(period)
    payment_data = get_payments_data(period)
    
    
    start_date, end_date, period_text = get_date_range_for_period(period)
    user_data['period_text'] = period_text
    
    context = {
        CONTEXT_USER_DATA: user_data,
        CONTEXT_PAYMENT_DATA: payment_data,
        CONTEXT_TIME_PERIOD: period,
        'active_section': 'users',
        'user_data_json': serialize_dashboard_data(user_data),
        'payment_data_json': serialize_dashboard_data(payment_data)
    }
    
    return render(request, TEMPLATE_USER_STATS, context)

@login_required
@user_passes_test(is_admin)
def report_detail(request, pk):
    """
    Vista para ver y responder a un reporte específico
    """
    report = get_report_by_id(pk)
    
    if not report:
        messages.error(request, "Reporte no encontrado")
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST' and 'response' in request.POST:
        response_text = request.POST.get('response')
        if update_report_status(report, response_text, request.user):
            messages.success(request, "Respuesta enviada con éxito")
        else:
            messages.error(request, "Error al responder al reporte")
    
    context = {
        'report': report,
        'active_section': 'reports'
    }
    
    return render(request, TEMPLATE_REPORT_DETAIL, context)

@login_required
@user_passes_test(is_admin)
def mark_report(request, pk):
    """
    Vista para marcar un reporte como leído/no leído
    """
    from reports.public import toggle_report_read_status
    
    report = get_report_by_id(pk)
    
    if not report:
        messages.error(request, "Reporte no encontrado")
    else:
        new_status = toggle_report_read_status(report)
        status_text = "leído" if new_status else "no leído"
        messages.success(request, f"Reporte marcado como {status_text}")
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:report_stats'))

@login_required
@user_passes_test(is_admin)
def get_trip_data_json(request):
    """
    Endpoint API para obtener datos de viajes en formato JSON
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    data = get_rides_data(period)
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def get_message_data_json(request):
    """
    Endpoint API para obtener datos de mensajes en formato JSON
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    data = get_messages_data(period)
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def get_report_data_json(request):
    """
    Endpoint API para obtener datos de reportes en formato JSON
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    data = get_reports_data(period)
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def get_user_data_json(request):
    """
    Endpoint API para obtener datos de usuarios en formato JSON
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    data = get_users_data(period)
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def get_payment_data_json(request):
    """
    Endpoint API para obtener datos de pagos en formato JSON
    """
    period = request.GET.get('period', DEFAULT_PERIOD)
    data = get_payments_data(period)
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def get_chat_messages(request, chat_id):
    """
    API para obtener los mensajes de un chat específico
    """
    from chat.models import Chat
    from chat._utils import get_messages_for_chat
    
    chat = get_object_or_404(Chat, id=chat_id)
    messages_data = get_messages_for_chat(chat)
    
    return JsonResponse({
        'messages': messages_data,
        'participants': [user.username for user in chat.participants.all()]
    })
