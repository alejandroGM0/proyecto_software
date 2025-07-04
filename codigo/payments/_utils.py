# ==========================================
# Autor: David Colás Martín
# ==========================================
import stripe
from django.conf import settings
from django.urls import reverse
from rides.models import Ride

print(f"Configurando Stripe con clave: {settings.STRIPE_SECRET_KEY[:5]}...")
stripe.api_key = settings.STRIPE_SECRET_KEY

try:
    stripe.PaymentMethod.list(limit=1)
    print("Conexión con Stripe establecida correctamente")
except Exception as e:
    print(f"ERROR conectando con Stripe: {str(e)}")


def create_checkout_session(payment, request):
    """
    Crea una sesión de checkout en Stripe para redireccionar al usuario.
    Utiliza Stripe Connect para transferir el dinero directamente al destinatario.

    Args:
        payment: Objeto modelo Payment que se va a procesar
        request: Objeto request de Django para construir URLs

    Returns:
        URL de redirección de Stripe
    """
    domain_url = f"{request.scheme}://{request.get_host()}"
    success_url = domain_url + reverse("payments:payment_success", args=[payment.id])
    cancel_url = domain_url + reverse("payments:payment_cancel", args=[payment.id])

    metadata = {
        "payment_id": str(payment.id),
    }

    if payment.ride:
        ride = payment.ride
        metadata.update(
            {
                "ride_id": str(ride.id),
                "origin": ride.origin,
                "destination": ride.destination,
            }
        )
        description = f"Pago de viaje: {ride.origin} → {ride.destination}"
    else:
        description = f"Pago #{payment.id}"

    # Comprobar si el destinatario tiene cuenta de Stripe Connect
    recipient_profile = payment.recipient.profile
    if not recipient_profile.stripe_account_id:
        print(
            f"El destinatario {payment.recipient.username} no tiene cuenta de Stripe Connect"
        )
        return None

    # Comprobar si el pagador tiene cuenta de cliente de Stripe
    payer_profile = payment.payer.profile

    # Calcular comisión de la plataforma
    # 10% para la plataforma
    from decimal import Decimal

    platform_fee = int(payment.amount * Decimal("100") * Decimal("0.10"))  # En céntimos

    checkout_params = {
        "payment_method_types": ["card", "paypal", "sepa_debit", "sofort"],
        "line_items": [
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": description,
                        "metadata": metadata,
                    },
                    "unit_amount": int(payment.amount * 100),  # En céntimos
                },
                "quantity": 1,
            }
        ],
        "metadata": metadata,
        "mode": "payment",
        "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": cancel_url,
        "payment_intent_data": {
            "application_fee_amount": platform_fee,
            "transfer_data": {
                "destination": recipient_profile.stripe_account_id,
            },
        },
    }

    if payer_profile.stripe_customer_id:
        checkout_params["customer"] = payer_profile.stripe_customer_id
    elif payment.payer.email:
        checkout_params["customer_email"] = payment.payer.email

    try:
        checkout_session = stripe.checkout.Session.create(**checkout_params)

        payment.stripe_payment_intent_id = checkout_session.id
        payment.save(update_fields=["stripe_payment_intent_id"])

        # Marcar que el usuario tiene método de pago
        if (
            not payer_profile.has_payment_method
            and checkout_session.payment_status == "paid"
        ):
            payer_profile.has_payment_method = True
            payer_profile.save(update_fields=["has_payment_method"])

        return checkout_session.url

    except Exception as e:
        print(f"Error creando sesión de Stripe: {str(e)}")
        return None


def get_payment_status(checkout_session_id):
    """
    Obtiene el estado de un pago desde Stripe
    """
    try:
        session = stripe.checkout.Session.retrieve(checkout_session_id)
        payment_intent = session.payment_intent

        if payment_intent:
            pi = stripe.PaymentIntent.retrieve(payment_intent)
            return pi.status
        return None
    except Exception as e:
        print(f"Error obteniendo estado de pago: {str(e)}")
        return None


def process_refund(payment):
    """
    Procesa un reembolso para un pago.
    Compatible con el sistema de pagos directo entre usuarios.
    """
    try:
        if not payment.stripe_payment_intent_id:
            return False, "No hay ID de pago de Stripe para procesar el reembolso"

        session = stripe.checkout.Session.retrieve(payment.stripe_payment_intent_id)
        payment_intent_id = session.payment_intent

        if not payment_intent_id:
            return False, "No se pudo encontrar el PaymentIntent asociado"

        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            reason="requested_by_customer",
        )

        return True, refund.id
    except Exception as e:
        return False, f"Error al procesar reembolso: {str(e)}"


def validate_payment_access(payment, user):
    """
    Verifica que el usuario tenga acceso al pago (como pagador o destinatario).

    Args:
        payment: Objeto Payment
        user: Usuario actual

    Returns:
        bool: True si el usuario tiene acceso, False en caso contrario
    """
    return payment.payer == user or payment.recipient == user


def validate_refund_permission(payment, user):
    """
    Verifica que el usuario pueda reembolsar el pago.

    Args:
        payment: Objeto Payment
        user: Usuario actual

    Returns:
        (bool, str): (Tiene permiso, Mensaje de error si no tiene permiso)
    """
    if payment.recipient != user:
        from .constants import ERROR_REFUND_PERMISSION

        return False, ERROR_REFUND_PERMISSION

    if payment.status != "COMPLETED":
        from .constants import ERROR_ONLY_COMPLETED

        return False, ERROR_ONLY_COMPLETED

    return True, None


def validate_cancel_permission(payment, user):
    """
    Verifica que el usuario pueda cancelar el pago.

    Args:
        payment: Objeto Payment
        user: Usuario actual

    Returns:
        (bool, str): (Tiene permiso, Mensaje de error si no tiene permiso)
    """
    if payment.payer != user:
        from .constants import ERROR_CANCEL_PERMISSION

        return False, ERROR_CANCEL_PERMISSION

    if payment.status != "PENDING":
        from .constants import ERROR_ONLY_PENDING

        return False, ERROR_ONLY_PENDING

    return True, None


def format_payment_description(payment):
    """
    Genera una descripción formateada para el pago.
    """
    try:
        from rides.models import Ride

        if isinstance(payment, Ride):
            return f"Pago de viaje: {payment.origin} → {payment.destination}"
        elif hasattr(payment, "ride") and payment.ride:
            return f"Pago de viaje: {payment.ride.origin} → {payment.ride.destination}"
        else:
            return f"Pago #{payment.id}"
    except Exception as e:
        print(f"Error en format_payment_description: {str(e)}")
        return "Pago de viaje"
