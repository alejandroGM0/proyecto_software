# ==========================================
# Autor: David Colás Martín
# ==========================================
# Estados de pago
PAYMENT_STATUS_PENDING = "PENDING"
PAYMENT_STATUS_COMPLETED = "COMPLETED"
PAYMENT_STATUS_FAILED = "FAILED"
PAYMENT_STATUS_REFUNDED = "REFUNDED"
PAYMENT_STATUS_CANCELLED = "CANCELLED"

PAYMENT_STATUS_CHOICES = [
    (PAYMENT_STATUS_PENDING, "Pendiente"),
    (PAYMENT_STATUS_COMPLETED, "Completado"),
    (PAYMENT_STATUS_FAILED, "Fallido"),
    (PAYMENT_STATUS_REFUNDED, "Reembolsado"),
    (PAYMENT_STATUS_CANCELLED, "Cancelado"),
]

# Métodos de pago
PAYMENT_METHOD_CREDIT_CARD = "CREDIT_CARD"
PAYMENT_METHOD_BANK_TRANSFER = "BANK_TRANSFER"
PAYMENT_METHOD_PAYPAL = "PAYPAL"
PAYMENT_METHOD_STRIPE = "STRIPE"

PAYMENT_METHOD_CHOICES = [
    (PAYMENT_METHOD_CREDIT_CARD, "Tarjeta de crédito"),
    (PAYMENT_METHOD_BANK_TRANSFER, "Transferencia bancaria"),
    (PAYMENT_METHOD_PAYPAL, "PayPal"),
    (PAYMENT_METHOD_STRIPE, "Stripe"),
]

# Mensajes comunes
ERROR_OWN_RIDE_PAYMENT = "No puedes pagar tu propio viaje"
ERROR_PERMISSION_DENIED = "No tienes permiso para ver este pago"
ERROR_REFUND_PERMISSION = "No tienes permiso para reembolsar este pago"
ERROR_CANCEL_PERMISSION = "No tienes permiso para cancelar este pago"
ERROR_ALREADY_PAID = "Ya has pagado este viaje"
ERROR_PAYMENT_PENDING = "Ya tienes un pago pendiente para este viaje"
ERROR_PAYMENT_PROCESSING = (
    "Hubo un error al procesar el pago. Por favor, inténtalo de nuevo."
)
ERROR_ONLY_COMPLETED = "Solo se pueden reembolsar pagos completados"
ERROR_ONLY_PENDING = "Solo se pueden cancelar pagos pendientes"

SUCCESS_PAYMENT_COMPLETED = "¡Pago completado con éxito!"
SUCCESS_PAYMENT_REFUNDED = "El pago ha sido reembolsado con éxito"
SUCCESS_PAYMENT_CANCELLED = "El pago ha sido cancelado con éxito"
INFO_PAYMENT_CANCELLED = "El proceso de pago ha sido cancelado"
INFO_PAYMENT_VERIFYING = (
    "El estado del pago está siendo verificado. Te notificaremos cuando se confirme."
)
