"""
Constantes para los tests de pagos.
"""
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# Usuarios
PAYER_USERNAME = 'pagador'
PAYER_EMAIL = 'pagador@example.com'
PAYER_PASSWORD = 'contraseña123'

RECIPIENT_USERNAME = 'receptor'
RECIPIENT_EMAIL = 'receptor@example.com'
RECIPIENT_PASSWORD = 'contraseña123'

ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@example.com'
ADMIN_PASSWORD = 'admin123'

# Viaje
RIDE_ORIGIN = 'Madrid'
RIDE_DESTINATION = 'Barcelona'
RIDE_PRICE = Decimal('25.50')
RIDE_DAYS_FUTURE = 2

# Pagos
PAYMENT_AMOUNT = Decimal('25.50')
PAYMENT_CONCEPT = 'Pago por viaje'
PAYMENT_NOTES = 'Notas sobre el pago'

PAYMENT_STRIPE_ID = 'pi_test_12345'
PAYMENT_REFUND_ID = 're_test_12345'

# Estados de pago
PAYMENT_STATUS_PENDING = 'PENDING'
PAYMENT_STATUS_COMPLETED = 'COMPLETED'
PAYMENT_STATUS_FAILED = 'FAILED'
PAYMENT_STATUS_REFUNDED = 'REFUNDED'
PAYMENT_STATUS_CANCELLED = 'CANCELLED'

# Métodos de pago
PAYMENT_METHOD_CREDIT_CARD = 'CREDIT_CARD'
PAYMENT_METHOD_BANK_TRANSFER = 'BANK_TRANSFER'
PAYMENT_METHOD_PAYPAL = 'PAYPAL'
PAYMENT_METHOD_STRIPE = 'STRIPE'

# Mensajes de error para pruebas
ERROR_REFUND_PERMISSION = "No tienes permiso para reembolsar este pago"
ERROR_ONLY_COMPLETED = "Solo se pueden reembolsar pagos completados"
ERROR_CANCEL_PERMISSION = "No tienes permiso para cancelar este pago"
ERROR_ONLY_PENDING = "Solo se pueden cancelar pagos pendientes"

# URLs
URL_PAYMENT_LIST = 'payments:payment_list'
URL_PAYMENT_HISTORY = 'payments:payment_history'
URL_PAYMENT_DETAIL = 'payments:payment_detail'
URL_CREATE_PAYMENT = 'payments:create_payment'
URL_PAYMENT_SUCCESS = 'payments:payment_success'
URL_PAYMENT_CANCEL = 'payments:payment_cancel'
URL_CANCEL_PAYMENT = 'payments:cancel_payment'
URL_REFUND_PAYMENT = 'payments:refund_payment'

# Templates
TEMPLATE_PAYMENT_LIST = 'payments/payment_list.html'
TEMPLATE_PAYMENT_HISTORY = 'payments/payment_history.html'
TEMPLATE_PAYMENT_DETAIL = 'payments/payment_detail.html'
TEMPLATE_CREATE_PAYMENT = 'payments/create_payment.html'
TEMPLATE_CANCEL_PAYMENT = 'payments/cancel_payment.html'
TEMPLATE_REFUND_PAYMENT = 'payments/refund_payment.html'
