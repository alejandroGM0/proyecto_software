"""
Módulo para exponer configuraciones públicas relacionadas con pagos.
"""
from django.conf import settings

# Clave pública de Stripe para usar en el frontend
STRIPE_PUBLIC_KEY = getattr(settings, 'STRIPE_PUBLIC_KEY', '')

def is_stripe_configured():
    """
    Verifica si las claves de Stripe están configuradas en el proyecto.
    """
    return bool(STRIPE_PUBLIC_KEY) and hasattr(settings, 'STRIPE_SECRET_KEY')

def get_payment_status_color(status):
    """
    Devuelve la clase CSS correspondiente al estado del pago.
    
    Args:
        status: Estado del pago (PENDING, COMPLETED, etc.)
        
    Returns:
        str: Clase CSS para el color del estado
    """
    # Convertir a mayúsculas para asegurar consistencia
    status = status.upper() if status else ''
    
    status_colors = {
        'PENDING': 'warning',
        'COMPLETED': 'success',
        'FAILED': 'danger', 
        'REFUNDED': 'info',
        'CANCELLED': 'secondary'
    }
    return status_colors.get(status, 'secondary')

def get_payment_status_display(status):
    """
    Devuelve la traducción del estado del pago para mostrar en la interfaz.
    """
    from .constants import PAYMENT_STATUS_CHOICES
    # Convertir a mayúsculas para asegurar consistencia
    status = status.upper() if status else ''
    
    status_dict = dict(PAYMENT_STATUS_CHOICES)
    return status_dict.get(status, status)
