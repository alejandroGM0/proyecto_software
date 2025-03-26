"""
API pública de la aplicación de reportes.
"""
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from .models import Report
from .constants import (
    PAYMENT_TYPE, RIDE_TYPE, USER_TYPE, SYSTEM_TYPE,
    NORMAL_IMPORTANCE, IMPORTANT_IMPORTANCE, URGENT_IMPORTANCE
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
        report_type=USER_TYPE,
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
        report_type=RIDE_TYPE,
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
        report_type=PAYMENT_TYPE,
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