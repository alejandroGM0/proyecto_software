# ==========================================
# Autor: David Colás Martín
# ==========================================
"""
API pública para la aplicación de pagos (payments).
"""
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db.models import Count, Q, Sum
from django.utils import timezone

from .constants import PAYMENT_STATUS_COMPLETED, PAYMENT_STATUS_REFUNDED
from .models import Payment

# Clave pública de Stripe para usar en el frontend
STRIPE_PUBLIC_KEY = getattr(settings, "STRIPE_PUBLIC_KEY", "")


def is_stripe_configured():
    """
    Verifica si las claves de Stripe están configuradas en el proyecto.
    """
    return bool(STRIPE_PUBLIC_KEY) and hasattr(settings, "STRIPE_SECRET_KEY")


def get_payment_status_color(status):
    """
    Devuelve la clase CSS correspondiente al estado del pago.
    """
    # Convertir a mayúsculas para asegurar consistencia
    status = status.upper() if status else ""

    status_colors = {
        "PENDING": "warning",
        "COMPLETED": "success",
        "FAILED": "danger",
        "REFUNDED": "info",
        "CANCELLED": "secondary",
    }
    return status_colors.get(status, "secondary")


def get_payment_status_display(status):
    """
    Devuelve la traducción del estado del pago para mostrar en la interfaz.
    """
    from .constants import PAYMENT_STATUS_CHOICES

    # Convertir a mayúsculas para asegurar consistencia
    status = status.upper() if status else ""

    status_dict = dict(PAYMENT_STATUS_CHOICES)
    return status_dict.get(status, status)


def get_payments_stats():
    """
    Obtiene estadísticas básicas de pagos en el sistema.
    """
    total_payments = Payment.objects.count()
    completed_payments = Payment.objects.filter(status=PAYMENT_STATUS_COMPLETED).count()
    total_amount = Payment.objects.filter(status=PAYMENT_STATUS_COMPLETED).aggregate(
        Sum("amount")
    )["amount__sum"] or Decimal("0")

    return {
        "total_payments": total_payments,
        "completed_payments": completed_payments,
        "total_amount": float(total_amount),
    }


def get_payments_in_period(start_date=None, end_date=None):
    """
    Devuelve los pagos realizados en un período específico.
    """
    queryset = Payment.objects.all()

    # Filtrar por fecha si se proporciona
    if start_date:
        queryset = queryset.filter(Q(created_at__date__gte=start_date))

    if end_date:
        queryset = queryset.filter(Q(created_at__date__lte=end_date))

    return queryset


def get_recent_payments(days=7, limit=5):
    """
    Obtiene los pagos más recientes realizados en los últimos días especificados.
    """
    recent_date = timezone.now() - timedelta(days=7)
    return Payment.objects.filter(created_at__gte=recent_date).order_by("-created_at")[
        :limit
    ]


def update_payments_on_booking_cancel(user, ride):
    """
    Actualiza el estado de los pagos asociados a un usuario y un viaje cuando
    se cancela una reserva de viaje.

    """
    payments = Payment.objects.filter(
        payer=user,
        ride=ride,
    )

    count = 0
    for payment in payments:
        payment.status = PAYMENT_STATUS_REFUNDED
        payment.save()
        count += 1

    return count
