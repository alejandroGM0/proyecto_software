# ==========================================
# Autor: David Colás Martín
# ==========================================
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from payments.models import Payment
from payments.tests.test_constants import *
from rides.models import Ride


class PaymentModelTests(TestCase):
    """
    Pruebas para el modelo Payment.
    """

    def setUp(self):
        """
        Configura los datos iniciales para las pruebas.
        """
        print("\nConfigurando pruebas para el modelo Payment...")

        # Crear usuarios
        self.payer = User.objects.create_user(
            username=PAYER_USERNAME, email=PAYER_EMAIL, password=PAYER_PASSWORD
        )

        self.recipient = User.objects.create_user(
            username=RECIPIENT_USERNAME,
            email=RECIPIENT_EMAIL,
            password=RECIPIENT_PASSWORD,
        )

        # Crear viaje
        self.future_date = timezone.now() + timedelta(days=RIDE_DAYS_FUTURE)
        self.ride = Ride.objects.create(
            driver=self.recipient,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=self.future_date,
            price=RIDE_PRICE,
            total_seats=4,
        )

        # Crear pagos
        self.pending_payment = Payment.objects.create(
            payer=self.payer,
            recipient=self.recipient,
            amount=PAYMENT_AMOUNT,
            ride=self.ride,
            status=PAYMENT_STATUS_PENDING,
            payment_method=PAYMENT_METHOD_STRIPE,
            concept=PAYMENT_CONCEPT,
        )

        self.completed_payment = Payment.objects.create(
            payer=self.payer,
            recipient=self.recipient,
            amount=PAYMENT_AMOUNT,
            ride=self.ride,
            status=PAYMENT_STATUS_COMPLETED,
            payment_method=PAYMENT_METHOD_CREDIT_CARD,
            concept=PAYMENT_CONCEPT,
            stripe_payment_intent_id=PAYMENT_STRIPE_ID,
        )

        self.refunded_payment = Payment.objects.create(
            payer=self.payer,
            recipient=self.recipient,
            amount=PAYMENT_AMOUNT,
            ride=self.ride,
            status=PAYMENT_STATUS_REFUNDED,
            payment_method=PAYMENT_METHOD_CREDIT_CARD,
            concept=PAYMENT_CONCEPT,
            stripe_payment_intent_id=PAYMENT_STRIPE_ID,
            stripe_refund_id=PAYMENT_REFUND_ID,
        )

        print(f"Creados {Payment.objects.count()} pagos para pruebas.")

    def test_payment_creation(self):
        """
        Verifica que los pagos se crean correctamente.
        """
        print("\nProbando la creación de pagos...")

        self.assertEqual(self.pending_payment.payer, self.payer)
        self.assertEqual(self.pending_payment.recipient, self.recipient)
        self.assertEqual(self.pending_payment.amount, PAYMENT_AMOUNT)
        self.assertEqual(self.pending_payment.ride, self.ride)
        self.assertEqual(self.pending_payment.status, PAYMENT_STATUS_PENDING)
        self.assertEqual(self.pending_payment.payment_method, PAYMENT_METHOD_STRIPE)
        self.assertEqual(self.pending_payment.concept, PAYMENT_CONCEPT)

        self.assertEqual(self.completed_payment.status, PAYMENT_STATUS_COMPLETED)
        self.assertEqual(
            self.completed_payment.stripe_payment_intent_id, PAYMENT_STRIPE_ID
        )

        self.assertEqual(self.refunded_payment.status, PAYMENT_STATUS_REFUNDED)
        self.assertEqual(self.refunded_payment.stripe_refund_id, PAYMENT_REFUND_ID)

    def test_string_representation(self):
        """
        Verifica la representación en string del modelo.
        """
        print("\nProbando la representación en string...")

        expected = f"Pago #{self.pending_payment.id} - {PAYMENT_AMOUNT}€ de {PAYER_USERNAME} a {RECIPIENT_USERNAME}"
        self.assertEqual(str(self.pending_payment), expected)

    def test_get_absolute_url(self):
        """
        Verifica que get_absolute_url devuelve la URL correcta.
        """
        print("\nProbando get_absolute_url...")

        expected_url = f"/payments/{self.pending_payment.id}/"
        self.assertTrue(self.pending_payment.get_absolute_url().endswith(expected_url))

    def test_get_status_display(self):
        """
        Verifica que get_status_display devuelve el texto correcto.
        """
        print("\nProbando get_status_display...")

        self.assertEqual(self.pending_payment.get_status_display(), "Pendiente")
        self.assertEqual(self.completed_payment.get_status_display(), "Completado")
        self.assertEqual(self.refunded_payment.get_status_display(), "Reembolsado")

        # Probar con un estado en minúscula (debería seguir funcionando)
        self.pending_payment.status = "pending"
        self.pending_payment.save()
        self.pending_payment.refresh_from_db()
        # Al guardar, el status se convierte a mayúsculas por el método save
        self.assertEqual(self.pending_payment.status, "PENDING")
        self.assertEqual(self.pending_payment.get_status_display(), "Pendiente")
