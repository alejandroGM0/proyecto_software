"""
API pública de la aplicación de reportes (reports).
"""
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count
from django.db.models.functions import TruncDate, TruncMonth, TruncYear, ExtractHour

from .models import Report
from .constants import (
    NORMAL_IMPORTANCE, IMPORTANT_IMPORTANCE, URGENT_IMPORTANCE,
    USER_REPORT, RIDE_REPORT, PAYMENT_REPORT, SYSTEM_REPORT
)

def get_report_by_id(report_id):
    """
    Obtiene un reporte por su ID.
    """
    try:
        return Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return None

def get_user_reports(user):
    """
    Obtiene todos los reportes creados por un usuario.
    """
    return Report.objects.filter(user=user).order_by('-created_at')

def get_reports_about_user(user):
    """
    Obtiene todos los reportes sobre un usuario específico.
    """
    return Report.objects.filter(reported_user=user).order_by('-created_at')

def get_reports_about_ride(ride):
    """
    Obtiene todos los reportes sobre un viaje específico.
    """
    return Report.objects.filter(ride=ride).order_by('-created_at')

def get_reports_about_payment(payment):
    """
    Obtiene todos los reportes sobre un pago específico.
    """
    return Report.objects.filter(payment=payment).order_by('-created_at')

def get_reports_count():
    """
    Obtiene el número total de reportes en el sistema.
    """
    return Report.objects.count()

def get_unread_reports_count():
    """
    Obtiene el número de reportes no leídos.
    """
    return Report.objects.filter(read=False).count()

def get_reports_by_type(report_type):
    """
    Obtiene reportes por tipo.
    """
    return Report.objects.filter(report_type=report_type).order_by('-created_at')

def get_reports_by_importance(importance):
    """
    Obtiene reportes por nivel de importancia.
    """
    return Report.objects.filter(importance=importance).order_by('-created_at')

def get_reports_with_response():
    """
    Obtiene reportes que tienen una respuesta.
    """
    return Report.objects.exclude(response__isnull=True).exclude(response='').order_by('-created_at')

def get_reports_without_response():
    """
    Obtiene reportes que no tienen una respuesta.
    """
    return Report.objects.filter(Q(response__isnull=True) | Q(response='')).order_by('-created_at')

def search_reports(query):
    """
    Busca reportes por título o descripción.
    """
    return Report.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query)
    ).order_by('-created_at')

def can_view_report(user, report):
    """
    Verifica si un usuario puede ver un reporte.
    """
    return user.is_staff or user == report.user

def can_edit_report(user, report):
    """
    Verifica si un usuario puede editar un reporte.
    """
    if report.response and not user.is_staff:
        return False
    return user.is_staff or user == report.user

def can_delete_report(user, report):
    """
    Verifica si un usuario puede eliminar un reporte.
    """
    return user.is_staff or user == report.user

def create_user_report(user, reported_user, title, description, importance=NORMAL_IMPORTANCE):
    """
    Crea un reporte sobre un usuario.
    """
    return Report.objects.create(
        title=title,
        description=description,
        report_type=USER_REPORT,
        importance=importance,
        user=user,
        reported_user=reported_user
    )

def create_ride_report(user, ride, title, description, importance=NORMAL_IMPORTANCE):
    """
    Crea un reporte sobre un viaje.
    """
    return Report.objects.create(
        title=title,
        description=description,
        report_type=RIDE_REPORT,
        importance=importance,
        user=user,
        ride=ride
    )

def create_payment_report(user, payment, title, description, importance=NORMAL_IMPORTANCE):
    """
    Crea un reporte sobre un pago.
    """
    return Report.objects.create(
        title=title,
        description=description,
        report_type=PAYMENT_REPORT,
        importance=importance,
        user=user,
        payment=payment
    )

def respond_to_report(admin_user, report, response_text):
    """
    Responde a un reporte.
    """
    if not admin_user.is_staff:
        return False
        
    report.response = response_text
    report.response_by = admin_user
    report.response_at = timezone.now()
    report.read = True
    report.save()
    return True

def mark_report_as_read(report):
    """
    Marca un reporte como leído.
    """
    report.read = True
    report.save(update_fields=['read'])
    return True

def mark_report_as_unread(report):
    """
    Marca un reporte como no leído.
    """
    report.read = False
    report.save(update_fields=['read'])
    return True

def update_report_status(report, response_text=None, admin_user=None, status_read=None):
    """
    Actualiza el estado de un reporte, opcionalmente añadiendo una respuesta.
    """
    try:
        if response_text and admin_user:
            if not admin_user.is_staff:
                return False
                
            report.response = response_text
            report.response_by = admin_user
            report.response_at = timezone.now()
            report.read = True
            
        elif status_read is not None:
            report.read = status_read
            
        report.save()
        return True
    except Exception:
        return False

def get_reports_in_period(start_date, end_date):
    """
    Obtiene los reportes creados en un período específico de tiempo.
    """
    reports = Report.objects.all()
    
    if start_date:
        reports = reports.filter(created_at__date__gte=start_date)
    
    if end_date:
        reports = reports.filter(created_at__date__lte=end_date)
    
    return reports.order_by('-created_at')

def get_reports_count_by_importance(reports):
    """
    Obtiene el conteo de reportes por nivel de importancia.
    """
    importance_counts = [0, 0, 0]  
    
    normal_count = reports.filter(importance=NORMAL_IMPORTANCE).count()
    important_count = reports.filter(importance=IMPORTANT_IMPORTANCE).count()
    urgent_count = reports.filter(importance=URGENT_IMPORTANCE).count()
    
    importance_counts[0] = normal_count
    importance_counts[1] = important_count
    importance_counts[2] = urgent_count
    
    return importance_counts

def get_daily_report_counts(reports, start_date, end_date):
    """
    Obtiene conteos diarios de reportes en un rango de fechas.
    """
    
    if hasattr(start_date, 'date'):
        start_date = start_date.date()
    if hasattr(end_date, 'date'):
        end_date = end_date.date()
        
    
    day_counts = reports.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    
    print(f"Reportes totales: {reports.count()}")
    print(f"Conteos por día: {list(day_counts)}")
    
    
    result = {}
    
    
    current_date = start_date
    while current_date <= end_date:
        date_key = current_date.strftime('%Y-%m-%d')
        result[date_key] = 0
        current_date += timedelta(days=1)
    
    
    for entry in day_counts:
        if entry['date']:
            date_key = entry['date'].strftime('%Y-%m-%d')
            result[date_key] = entry['count']
    
    return result

def get_hourly_report_counts(reports, date):
    """
    Obtiene conteos de reportes por hora para un día específico.
    """
    hourly_data = [0] * 24
    
    hour_counts = reports.filter(
        created_at__date=date
    ).annotate(
        hour=ExtractHour('created_at')
    ).values('hour').annotate(count=Count('id'))
    
    for entry in hour_counts:
        hour = entry['hour']
        if 0 <= hour < 24:
            hourly_data[hour] = entry['count']
    
    return hourly_data

def get_monthly_report_counts(reports, start_date, end_date):
    """
    Obtiene conteos mensuales de reportes en un rango de fechas.
    """
    month_counts = reports.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    result = {}
    print("Month counts:", month_counts)  
    for entry in month_counts:
        if entry['month']:
            month_key = entry['month'].strftime('%b %Y')
            result[month_key] = entry['count']
    
    return result