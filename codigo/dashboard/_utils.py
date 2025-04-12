# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
Utilidades para la aplicación de dashboard
"""
import json
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth, ExtractHour
from django.utils import timezone


from rides.public import get_rides_in_period, get_ride_stats_for_dashboard, get_recently_published_rides
from chat.public import get_messages_in_period
from reports.public import get_reports_in_period
from accounts.public import get_users_in_period, get_active_users
from payments.public import get_payments_in_period
from chat.public import filter_chats_by_criteria, get_chat_stats
from django.core.paginator import Paginator
import json
from django.core.serializers.json import DjangoJSONEncoder
from reports.public import (
        get_hourly_report_counts, 
        get_daily_report_counts, 
        get_monthly_report_counts
    )
from .constants import (
    PERIOD_TODAY, PERIOD_WEEK, PERIOD_MONTH, PERIOD_YEAR, PERIOD_ALL,
    DEFAULT_PERIOD, CHART_COLORS, PERIOD_TEXT_TODAY, PERIOD_TEXT_WEEK,
    PERIOD_TEXT_MONTH, PERIOD_TEXT_YEAR, PERIOD_TEXT_ALL
)
from accounts.public import filter_users_by_criteria
from django.contrib.auth.models import User

def get_date_range_for_period(period):
    """
    Obtiene el rango de fechas según el período seleccionado
    """
    now = timezone.now()
    
    if period == PERIOD_TODAY:
        
        start_date = timezone.make_aware(datetime.combine(now.date(), datetime.min.time()))
        end_date = now
        period_text = PERIOD_TEXT_TODAY
    elif period == PERIOD_WEEK:
        
        start_date = now - timedelta(days=7)
        end_date = now
        period_text = PERIOD_TEXT_WEEK
    elif period == PERIOD_MONTH:
        
        start_date = now - timedelta(days=30)
        end_date = now
        period_text = PERIOD_TEXT_MONTH
    elif period == PERIOD_YEAR:
        
        start_date = now - timedelta(days=365)
        end_date = now
        period_text = PERIOD_TEXT_YEAR
    else:  
        
        start_date = timezone.make_aware(datetime(1970, 1, 1))
        end_date = now
        period_text = PERIOD_TEXT_ALL
    
    return start_date, end_date, period_text

def serialize_dashboard_data(data):
    """
    Serializa datos para su uso en JavaScript
    """
    return json.dumps(data, cls=DjangoJSONEncoder)

def get_date_range(period=DEFAULT_PERIOD):
    """
    Devuelve un rango de fechas basado en el período seleccionado
    """
    today = timezone.now().date()
    
    if period == PERIOD_TODAY:
        return today, today
    elif period == PERIOD_WEEK:
        week_ago = today - timedelta(days=7)
        return week_ago, today
    elif period == PERIOD_MONTH:
        month_ago = today - timedelta(days=30)
        return month_ago, today
    elif period == PERIOD_YEAR:
        year_ago = today - timedelta(days=365)
        return year_ago, today
    else:  
        return None, today

def get_last_n_days(n=7):
    """
    Devuelve una lista de los últimos n días en formato string
    """
    today = timezone.now().date()
    return [(today - timedelta(days=i)).strftime('%d/%m') for i in range(n-1, -1, -1)]

def get_hourly_labels(date):
    """
    Devuelve una lista de 24 horas en formato string para el día especificado
    """
    return [f"{hour:02d}:00" for hour in range(24)]

def get_daily_labels(start_date, end_date):
    """
    Devuelve una lista de días entre dos fechas en formato string
    """
    days_diff = (end_date - start_date).days + 1
    return [(start_date + timedelta(days=i)).strftime('%d/%m') for i in range(days_diff)]

def get_monthly_labels(start_date, end_date):
    """
    Devuelve una lista de meses entre dos fechas en formato string
    """
    months = []
    current_date = start_date.replace(day=1)
    end_month_date = end_date.replace(day=28) + timedelta(days=4)
    end_month_date = end_month_date.replace(day=1)
    
    while current_date <= end_month_date:
        months.append(current_date.strftime('%b %Y'))
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return months

def get_dashboard_data(period=DEFAULT_PERIOD, active_section=None):
    """
    Construye un diccionario con datos comunes para todas las vistas del dashboard
    """
    context = {}
    
    
    if active_section:
        context['active_section'] = active_section
    
    
    context['time_period'] = period
    context['available_periods'] = {
        PERIOD_TODAY: PERIOD_TEXT_TODAY,
        PERIOD_WEEK: PERIOD_TEXT_WEEK,
        PERIOD_MONTH: PERIOD_TEXT_MONTH,
        PERIOD_YEAR: PERIOD_TEXT_YEAR,
        PERIOD_ALL: PERIOD_TEXT_ALL
    }
    
    
    context['chart_colors'] = CHART_COLORS
    
    
    context['trip_data'] = get_rides_data(period)
    context['msg_data'] = get_messages_data(period)
    context['report_data'] = get_reports_data(period)
    context['user_data'] = get_users_data(period)
    context['payment_data'] = get_payments_data(period)
    
    return context

def get_rides_data(period=DEFAULT_PERIOD):
    """
    Obtiene datos de viajes según el período especificado
    """
    start_date, end_date = get_date_range(period)
    return get_ride_stats_for_dashboard(start_date, end_date)

def get_messages_data(period=DEFAULT_PERIOD):
    """
    Obtiene datos de mensajes según el período especificado
    """
    from chat.models import Message
    
    start_date, end_date = get_date_range(period)
    
    
    if start_date is not None:
        if not isinstance(start_date, datetime):
            try:
                
                start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            except (TypeError, AttributeError):
                
                start_datetime = start_date
        else:
            start_datetime = start_date
    else:
        start_datetime = None
        
    if end_date is not None:
        if not isinstance(end_date, datetime):
            try:
                
                end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
            except (TypeError, AttributeError):
                
                end_datetime = end_date
        else:
            end_datetime = end_date
    else:
        end_datetime = None
    
    
    if start_datetime and end_datetime:
        messages = Message.objects.filter(
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        )
    else:
        messages = Message.objects.all()
    
    
    total_messages = messages.count()
    
    
    if start_date and end_date:
        days_in_period = (end_date - start_date).days + 1
    else:
        days_in_period = 30  
    
    
    labels = []
    data = []
    
    if period == PERIOD_TODAY:
        
        labels = get_hourly_labels(timezone.now().date())
        hourly_data = [0] * 24
        
        
        if total_messages > 0:
            hour_counts = messages.annotate(
                hour=ExtractHour('created_at')
            ).values('hour').annotate(count=Count('id'))
            
            for entry in hour_counts:
                hour = entry['hour']
                if 0 <= hour < 24:
                    hourly_data[hour] = entry['count']
        
        data = hourly_data
        
    elif period in [PERIOD_WEEK, PERIOD_MONTH]:
        
        if start_date and end_date:
            labels = get_daily_labels(start_date, end_date)
            daily_data = [0] * len(labels)
            
            
            if total_messages > 0:
                day_counts = messages.annotate(
                    date=TruncDate('created_at')
                ).values('date').annotate(count=Count('id'))
                
                for i, label_date in enumerate([start_date + timedelta(days=i) for i in range(len(labels))]):
                    for entry in day_counts:
                        if entry['date'] == label_date:
                            daily_data[i] = entry['count']
                            break
            
            data = daily_data
    
    else:  
        
        if not start_date:
            start_date = end_date - timedelta(days=365)
            
        labels = get_monthly_labels(start_date, end_date)
        monthly_data = [0] * len(labels)
        
        
        if total_messages > 0:
            month_counts = messages.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(count=Count('id')).order_by('month')
            
            
            for entry in month_counts:
                month_str = entry['month'].strftime('%b %Y')
                if month_str in labels:
                    monthly_data[labels.index(month_str)] = entry['count']
        
        data = monthly_data
    
    
    _, _, period_text = get_date_range_for_period(period)
    
    return {
        'total': total_messages,
        'labels': labels,
        'data': data,
        'avg_per_day': round(total_messages / max(1, days_in_period)),  # Redondear a entero, sin el segundo parámetro
        'period': period,
        'period_text': period_text
    }

def get_reports_data(period=DEFAULT_PERIOD):
    """
    Obtiene datos de reportes según el período especificado
    """
    start_date, end_date = get_date_range(period)
    reports = get_reports_in_period(start_date, end_date)
    
    
    total, unread, without_response, importance_counts = get_basic_report_stats(reports)
    resolved = total - without_response
    
    
    labels, data = get_temporal_report_data(reports, period, start_date, end_date)
    
    
    print(f"Período: {period}, Total reportes: {total}, Datos: {data}")
    
    
    with_response = (resolved / total * 100) if total > 0 else 0
    
    
    _, _, period_text = get_date_range_for_period(period)
    
    return {
        'total': total,
        'unread': unread,
        'resolved': resolved,
        'by_type': list(reports.values('report_type').annotate(count=Count('id'))),
        'by_importance': list(reports.values('importance').annotate(count=Count('id'))),
        'period': period,
        'period_text': period_text,
        'created_in_period': total,
        'unread_reports': unread,
        'without_response': without_response,
        'total_reports': total,
        'with_response': round(with_response),
        'importance_counts': importance_counts,
        'labels': labels,
        'datasets': [{'data': data}] if data else []
    }

def get_basic_report_stats(reports):
    """
    Obtiene estadísticas básicas de un conjunto de reportes.
    """
    from reports.public import get_reports_count_by_importance
    
    total = reports.count()
    unread = reports.filter(read=False).count()
    without_response = reports.filter(
        Q(response__isnull=True) | Q(response='')
    ).count()
    
    importance_counts = get_reports_count_by_importance(reports)
    
    return total, unread, without_response, importance_counts

def get_temporal_report_data(reports, period, start_date, end_date):
    """
    Obtiene datos temporales para gráficos de reportes.
    """
    labels = []
    data = []
    
    ordered_reports = reports.order_by('created_at')
    total_reports = ordered_reports.count()
    
    
    print(f"Período: {period}, Total reportes en la consulta: {total_reports}")
    
    if period == PERIOD_TODAY:
        labels = get_hourly_labels(timezone.now().date())
        data = get_hourly_report_counts(ordered_reports, timezone.now().date())
        
    elif period in [PERIOD_WEEK, PERIOD_MONTH]:
        if start_date and end_date:
            if hasattr(start_date, 'date'):
                start_date = start_date.date()
            if hasattr(end_date, 'date'):
                end_date = end_date.date()
                
            labels = get_daily_labels(start_date, end_date)
            
            
            day_counts = get_daily_report_counts(ordered_reports, start_date, end_date)
            
            
            daily_data = []
            for i in range(len(labels)):
                current_date = start_date + timedelta(days=i)
                date_key = current_date.strftime('%Y-%m-%d')
                daily_data.append(day_counts.get(date_key, 0))
            
            
            total_in_chart = sum(daily_data)
            print(f"Total en el gráfico: {total_in_chart}, debería ser: {total_reports}")
            
            data = daily_data
    
    else:  
        if not start_date:
            start_date = end_date - timedelta(days=365)
            
        labels = get_monthly_labels(start_date, end_date)
        monthly_data = [0] * len(labels)
        
        month_counts = get_monthly_report_counts(ordered_reports, start_date, end_date)
        
        
        for i, month_str in enumerate(labels):
            if month_str in month_counts:
                monthly_data[i] = month_counts[month_str]
        
        data = monthly_data
    
    return labels, data

def process_daily_report_counts(reports, start_date, end_date):
    """
    Procesa los conteos diarios de reportes y los devuelve en un diccionario.S
    """
    
    day_counts = reports.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(count=Count('id'))
    
    
    result = {}
    for entry in day_counts:
        date_key = entry['date'].strftime('%Y-%m-%d')
        result[date_key] = entry['count']
    
    return result

def get_users_data(period=DEFAULT_PERIOD):
    """
    Obtiene datos de usuarios según el período especificado
    """
    from accounts.models import UserProfile
    from django.contrib.auth.models import User
    
    start_date, end_date = get_date_range(period)
    users = get_users_in_period(start_date, end_date)
    
    
    active_users = get_active_users(minutes=30).count()
    total_users = User.objects.count()
    registered_in_period = users.count()
    inactive_users = total_users - active_users
    
    
    
    profiles = UserProfile.objects.all()
    with_vehicle = profiles.filter(has_vehicle=True).count()
    
    
    top_locations = list(profiles.exclude(location='')
                         .exclude(location__isnull=True)
                         .values('location')
                         .annotate(count=Count('location'))
                         .order_by('-count')[:5])
    
    
    formatted_top_locations = [[item['location'], item['count']] for item in top_locations]
    
    
    labels = []
    data = []
    
    if period == PERIOD_TODAY:
        
        labels = get_hourly_labels(timezone.now().date())
        hourly_data = [0] * 24
        
        
        if registered_in_period > 0:
            hour_counts = users.annotate(
                hour=ExtractHour('date_joined')
            ).values('hour').annotate(count=Count('id'))
            
            for entry in hour_counts:
                hour = entry['hour']
                if 0 <= hour < 24:
                    hourly_data[hour] = entry['count']
        
        data = hourly_data
        
    elif period in [PERIOD_WEEK, PERIOD_MONTH]:
        
        if start_date and end_date:
            labels = get_daily_labels(start_date, end_date)
            daily_data = [0] * len(labels)
            
            
            if registered_in_period > 0:
                day_counts = users.annotate(
                    date=TruncDate('date_joined')
                ).values('date').annotate(count=Count('id'))
                
                for i, label_date in enumerate([start_date + timedelta(days=i) for i in range(len(labels))]):
                    for entry in day_counts:
                        if entry['date'] == label_date:
                            daily_data[i] = entry['count']
                            break
            
            data = daily_data
    
    else:  
        
        if not start_date:
            start_date = end_date - timedelta(days=365)
            
        labels = get_monthly_labels(start_date, end_date)
        monthly_data = [0] * len(labels)
        
        
        if registered_in_period > 0:
            month_counts = users.annotate(
                month=TruncMonth('date_joined')
            ).values('month').annotate(count=Count('id')).order_by('month')
            
            
            for entry in month_counts:
                month_str = entry['month'].strftime('%b %Y')
                if month_str in labels:
                    monthly_data[labels.index(month_str)] = entry['count']
        
        data = monthly_data
    
    
    
    driver_only = with_vehicle
    admin_users = User.objects.filter(is_staff=True).count()
    both_roles = User.objects.filter(is_staff=True, profile__has_vehicle=True).count()
    
    
    _, _, period_text = get_date_range_for_period(period)
    
    return {
        'total': total_users,
        'active': active_users,
        'inactive': inactive_users,
        'with_vehicle': with_vehicle,
        'period': period,
        
        'total_users': total_users,
        'registered_in_period': registered_in_period,
        'driver_only': driver_only,
        'both_roles': both_roles,
        'admin_users': admin_users,
        'top_locations': formatted_top_locations,
        'labels': labels,
        'datasets': [{'data': data}] if data else [],
        'period_text': period_text
    }

def get_payments_data(period=DEFAULT_PERIOD):
    """
    Obtiene datos de pagos según el período especificado
    """
    start_date, end_date = get_date_range(period)
    payments = get_payments_in_period(start_date, end_date)
    
    
    total = payments.count()
    amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    avg_per_transaction = amount / total if total > 0 else 0
    
    
    payments_by_status = list(payments.values('status').annotate(count=Count('id')))
    
    
    labels = []
    data = []
    
    if period == PERIOD_TODAY:
        
        labels = get_hourly_labels(timezone.now().date())
        hourly_data = [0] * 24
        
        
        if total > 0:
            hour_counts = payments.annotate(
                hour=ExtractHour('created_at')
            ).values('hour').annotate(count=Count('id'))
            
            for entry in hour_counts:
                hour = entry['hour']
                if 0 <= hour < 24:
                    hourly_data[hour] = entry['count']
        
        data = hourly_data
        
    elif period in [PERIOD_WEEK, PERIOD_MONTH]:
        
        if start_date and end_date:
            labels = get_daily_labels(start_date, end_date)
            daily_data = [0] * len(labels)
            
            
            if total > 0:
                day_counts = payments.annotate(
                    date=TruncDate('created_at')
                ).values('date').annotate(count=Count('id'))
                
                for i, label_date in enumerate([start_date + timedelta(days=i) for i in range(len(labels))]):
                    for entry in day_counts:
                        if entry['date'] == label_date:
                            daily_data[i] = entry['count']
                            break
            
            data = daily_data
    
    else:  
        
        if not start_date:
            start_date = end_date - timedelta(days=365)
            
        labels = get_monthly_labels(start_date, end_date)
        monthly_data = [0] * len(labels)
        
        
        if total > 0:
            month_counts = payments.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(count=Count('id')).order_by('month')
            
            
            for entry in month_counts:
                month_str = entry['month'].strftime('%b %Y')
                if month_str in labels:
                    monthly_data[labels.index(month_str)] = entry['count']
        
        data = monthly_data
    
    
    _, _, period_text = get_date_range_for_period(period)
    
    return {
        'total': total,
        'amount': amount,
        'avg_per_transaction': avg_per_transaction,
        'period': period,
        'period_text': period_text,
        'payments_by_status': payments_by_status,
        'labels': labels,
        'datasets': [{'data': data}] if data else []
    }

def get_filtered_reports(request):
    """
    Devuelve reportes filtrados según los parámetros de la solicitud
    """
    reports = get_reports_in_period(None, timezone.now().date())
    active_filters = {}
    
    
    if request and request.GET:
        status = request.GET.get('status')
        if status == 'unread':
            reports = reports.filter(read=False)
            active_filters['status'] = 'No leídos'
        elif status == 'read':
            reports = reports.filter(read=True)
            active_filters['status'] = 'Leídos'
        
        report_type = request.GET.get('type')
        if report_type:
            reports = reports.filter(report_type=report_type)
            active_filters['type'] = report_type
    
    return reports, active_filters

def get_db_status():
    """
    Comprueba el estado de la base de datos
    """
    from django.db import connection
    
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT 1')
        return {'status': 'good', 'message': 'Funcionando'}
    except Exception:
        return {'status': 'critical', 'message': 'Error de conexión'}

def get_websocket_status():
    """
    Comprueba el estado de las conexiones WebSocket
    """
    last_hour = timezone.now() - timedelta(hours=1)
    recent_messages = get_messages_in_period(last_hour, timezone.now())
    
    if recent_messages > 0:
        return {'status': 'good', 'message': f'Activas ({recent_messages} mensajes recientes)'}
    else:
        return {'status': 'warning', 'message': 'Sin actividad reciente'}

def get_payment_status():
    """
    Comprueba el estado del sistema de pagos
    """
    last_hour = timezone.now() - timedelta(hours=1)
    recent_payments = get_payments_in_period(last_hour, timezone.now()).count()
    
    if recent_payments > 0:
        return {'status': 'good', 'message': f'Procesando ({recent_payments} transacciones recientes)'}
    else:
        return {'status': 'good', 'message': 'Operativo'}

def get_server_performance_status():
    """
    Comprueba el rendimiento del servidor
    """
    import psutil
    
    cpu_percent = psutil.cpu_percent()
    if cpu_percent < 70:
        return {'status': 'good', 'message': 'Óptimo'}
    elif cpu_percent < 85:
        return {'status': 'warning', 'message': 'Moderado'}
    else:
        return {'status': 'critical', 'message': 'Sobrecargado'}

def get_storage_status():
    """
    Comprueba el estado del almacenamiento
    """
    import psutil
    
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    free_gb = round(disk.free / (1024 * 1024 * 1024), 1)  
    
    if disk_percent < 70:
        return {'status': 'good', 'message': f'{100-disk_percent}% disponible ({free_gb} GB)'}
    elif disk_percent < 85:
        return {'status': 'warning', 'message': f'{100-disk_percent}% disponible ({free_gb} GB)'}
    else:
        return {'status': 'critical', 'message': f'{100-disk_percent}% disponible ({free_gb} GB)'}

def get_memory_status():
    """
    Comprueba el estado de la memoria
    """
    import psutil
    
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    free_mb = round(memory.available / (1024 * 1024), 1)  
    
    if memory_percent < 70:
        return {'status': 'good', 'message': f'{100-memory_percent}% libre ({free_mb} MB)'}
    elif memory_percent < 85:
        return {'status': 'warning', 'message': f'{100-memory_percent}% libre ({free_mb} MB)'}
    else:
        return {'status': 'critical', 'message': f'{100-memory_percent}% libre ({free_mb} MB)'}

def get_uptime():
    """
    Obtiene el tiempo de actividad del servidor
    """
    import psutil
    from datetime import datetime
    
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    days = uptime.days
    seconds = uptime.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if days > 0:
        uptime_msg = f'{days} días, {hours} horas'
    else:
        uptime_msg = f'{hours} horas, {minutes} minutos'
    
    return {'status': 'info', 'message': uptime_msg}

def get_system_status():
    """
    Obtiene métricas reales del estado del sistema para mostrar en el dashboard.
    """
    status = {}
    
    status['database'] = get_db_status()
    status['websocket'] = get_websocket_status()
    status['payments'] = get_payment_status()
    status['performance'] = get_server_performance_status()
    status['storage'] = get_storage_status()
    status['memory'] = get_memory_status()
    status['uptime'] = get_uptime()
    
    return status

def get_recent_activities(include_rides=True):
    """
    Obtiene una lista de actividades recientes en el sistema
    Si include_rides es False, excluye la actividad de viajes
    """
    from accounts.public import get_recently_registered_users
    
    activities = []
    now = timezone.now()
    
    
    recent_users = get_recently_registered_users(days=1, limit=3)
    
    for user in recent_users:
        time_ago = now - user.date_joined
        minutes_ago = int(time_ago.total_seconds() / 60)
        
        if minutes_ago < 60:
            time_display = f"Hace {minutes_ago} minutos" if minutes_ago != 1 else "Hace 1 minuto"
        else:
            hours_ago = int(minutes_ago / 60)
            time_display = f"Hace {hours_ago} horas" if hours_ago != 1 else "Hace 1 hora"
        
        activities.append({
            'icon': 'fa-user-plus',
            'title': 'Nuevo registro de usuario',
            'description': f"Usuario '{user.username}' se ha registrado",
            'time_ago': time_display
        })
    
    
    if include_rides:
        recent_rides = get_recently_published_rides(limit=3)
        
        for ride in recent_rides:
            time_ago = now - ride.created_at
            minutes_ago = int(time_ago.total_seconds() / 60)
            
            if minutes_ago < 60:
                time_display = f"Hace {minutes_ago} minutos" if minutes_ago != 1 else "Hace 1 minuto"
            else:
                hours_ago = int(minutes_ago / 60)
                time_display = f"Hace {hours_ago} horas" if hours_ago != 1 else "Hace 1 hora"
            
            activities.append({
                'icon': 'fa-car',
                'title': 'Nuevo viaje publicado',
                'description': f"{ride.origin} → {ride.destination}, {ride.seats_available} plazas disponibles",
                'time_ago': time_display
            })
    
    
    activities.sort(key=lambda x: int(x['time_ago'].split(' ')[1]), reverse=False)
    
    return activities

def get_ride_activities():
    """
    Obtiene específicamente las actividades relacionadas con viajes más recientemente publicados 
    """
    activities = []
    now = timezone.now()
    
    
    recent_rides = get_recently_published_rides(limit=5)
    
    for ride in recent_rides:
        time_ago = now - ride.created_at
        minutes_ago = int(time_ago.total_seconds() / 60)
        
        if minutes_ago < 60:
            time_display = f"Hace {minutes_ago} minutos" if minutes_ago != 1 else "Hace 1 minuto"
        else:
            hours_ago = int(minutes_ago / 60)
            if hours_ago < 24:
                time_display = f"Hace {hours_ago} horas" if hours_ago != 1 else "Hace 1 hora"
            else:
                days_ago = int(hours_ago / 24)
                time_display = f"Hace {days_ago} días" if days_ago != 1 else "Hace 1 día"
        
        activities.append({
            'icon': 'fa-car',
            'title': 'Viaje recientemente publicado',
            'description': f"{ride.origin} → {ride.destination}, {ride.seats_available} plazas disponibles",
            'time_ago': time_display
        })
    
    return activities

def get_ride_management_context(request):
    """
    Función para obtener el contexto de gestión de viajes para el panel de administración
    """
    from rides.public import filter_rides_by_criteria, get_ride_stats
    from django.core.paginator import Paginator
    
    
    filters = {
        'search': request.GET.get('search', ''),
        'status': request.GET.get('status', 'all'),
        'origin': request.GET.get('origin', ''),
        'destination': request.GET.get('destination', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'active_section': 'ride_management'
    }
    
    
    rides_query = filter_rides_by_criteria(
        search=filters['search'],
        status=filters['status'],
        origin=filters['origin'],
        destination=filters['destination'],
        date_from=filters['date_from'],
        date_to=filters['date_to']
    )
    
    
    page_number = request.GET.get('page', 1)
    paginator = Paginator(rides_query, 10)  
    
    try:
        rides = paginator.page(page_number)
    except:
        rides = paginator.page(1)
    
    
    stats = get_ride_stats()
    
    
    from django.core.serializers.json import DjangoJSONEncoder
    top_destinations = list(rides_query.values('destination')
                        .annotate(count=Count('destination'))
                        .order_by('-count')[:5])
    
    top_origins = list(rides_query.values('origin')
                    .annotate(count=Count('origin'))
                    .order_by('-count')[:5])
    
    chart_data = {
        'top_destinations': json.dumps(top_destinations, cls=DjangoJSONEncoder),
        'top_origins': json.dumps(top_origins, cls=DjangoJSONEncoder)
    }
    
    return {
        'rides': rides,
        'filters': filters,
        'stats': stats,
        'chart_data': chart_data,
        'active_section': 'trips',
        'now': timezone.now()  
    }

def get_user_management_context(request):
    """
    Función para obtener el contexto de gestión de usuarios para el panel de administración
    """
    
    filters = {
        'search': request.GET.get('search', ''),
        'status': request.GET.get('status', 'all'),
        'from_date': request.GET.get('from_date', ''),
        'to_date': request.GET.get('to_date', ''),
        'active_section': 'user_management'
    }
    
    users_query = filter_users_by_criteria(
        search=filters['search'],
        status=filters['status'],
        from_date=filters['from_date'],
        to_date=filters['to_date']
    )
    
    page_number = request.GET.get('page', 1)
    paginator = Paginator(users_query, 10)  
    
    try:
        users = paginator.page(page_number)
    except:
        users = paginator.page(1)
    
    from accounts.models import UserProfile
    
    total_users = User.objects.count()
    active_users = len(get_active_users(minutes=30))
    staff_users = User.objects.filter(is_staff=True).count()
    with_vehicle = UserProfile.objects.filter(has_vehicle=True).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'with_vehicle': with_vehicle,
    }
    
    from django.db.models import Count
    
    top_locations = list(UserProfile.objects.exclude(location='')
                         .exclude(location__isnull=True)
                         .values('location')
                         .annotate(count=Count('location'))
                         .order_by('-count')[:5])
    
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    chart_data = {
        'top_locations': json.dumps(top_locations, cls=DjangoJSONEncoder),
    }
    
    return {
        'users': users,
        'filters': filters,
        'stats': stats,
        'chart_data': chart_data,
        'active_section': 'users',
        'now': timezone.now()
    }

def get_chat_management_context(request):
    """
    Función para obtener el contexto de gestión de chats para el panel de administración
    """
    
    filters = {
        'search': request.GET.get('search', ''),
        'chat_type': request.GET.get('chat_type', 'all'),
        'from_date': request.GET.get('from_date', ''),
        'to_date': request.GET.get('to_date', ''),
    }
    
    chats_data = filter_chats_by_criteria(
        search=filters['search'],
        chat_type=filters['chat_type'],
        from_date=filters['from_date'],
        to_date=filters['to_date']
    )
    
    page_number = request.GET.get('page', 1)
    paginator = Paginator(chats_data, 10)
    
    try:
        chats = paginator.page(page_number)
    except:
        chats = paginator.page(1)
    
    stats = get_chat_stats()
    
    return {
        'chats': chats,
        'filters': filters,
        'stats': stats,
        'active_section': 'chats',
        'now': timezone.now()
    }
