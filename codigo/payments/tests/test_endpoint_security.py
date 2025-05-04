# ==========================================
# Autor: David Colás Martín
# ==========================================
from datetime import timedelta
from unittest.mock import patch

from accounts.models import UserProfile
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from payments.models import Payment
from payments.tests.test_constants import *
from rides.models import Ride


class PaymentEndpointSecurityTests(TestCase):
    """
    Pruebas de seguridad para los endpoints del módulo de pagos.
    """

    def setUp(self):
        """
        Configura los datos iniciales para las pruebas de seguridad.
        """
        print("\nConfigurando pruebas de seguridad para endpoints de pagos...")

        self.client = Client()

        # Crear usuarios
        self.payer = User.objects.create_user(
            username=PAYER_USERNAME, email=PAYER_EMAIL, password=PAYER_PASSWORD
        )
        UserProfile.objects.create(user=self.payer)

        self.recipient = User.objects.create_user(
            username=RECIPIENT_USERNAME,
            email=RECIPIENT_EMAIL,
            password=RECIPIENT_PASSWORD,
        )
        UserProfile.objects.create(user=self.recipient)

        self.admin_user = User.objects.create_superuser(
            username=ADMIN_USERNAME, email=ADMIN_EMAIL, password=ADMIN_PASSWORD
        )
        UserProfile.objects.create(user=self.admin_user)

        self.other_user = User.objects.create_user(
            username="otro_usuario", email="otro@example.com", password="contraseña123"
        )
        UserProfile.objects.create(user=self.other_user)

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

        print(f"Creados {Payment.objects.count()} pagos para pruebas de seguridad.")

    def test_unauthorized_access_to_payment_list(self):
        """
        Prueba que un usuario no autenticado no puede acceder a la lista de pagos.
        """
        print("\nProbando acceso no autorizado a lista de pagos...")

        # Intentar acceder sin autenticación
        response = self.client.get(reverse(URL_PAYMENT_LIST))

        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/login/" in response.url)

    def test_unauthorized_access_to_payment_detail(self):
        """
        Prueba que un usuario no autenticado no puede acceder al detalle de un pago.
        """
        print("\nProbando acceso no autorizado a detalle de pago...")

        # Intentar acceder sin autenticación
        response = self.client.get(
            reverse(URL_PAYMENT_DETAIL, args=[self.completed_payment.id])
        )

        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/login/" in response.url)

    def test_unauthorized_user_access_to_others_payment(self):
        """
        Prueba que un usuario no puede ver pagos de otros usuarios.
        """
        print("\nProbando acceso de usuario no autorizado a pago ajeno...")

        # Login como otro usuario que no es ni pagador ni receptor
        self.client.login(username="otro_usuario", password="contraseña123")

        # Intentar ver el detalle de un pago
        response = self.client.get(
            reverse(URL_PAYMENT_DETAIL, args=[self.completed_payment.id])
        )

        # Debe redireccionar (acceso denegado)
        self.assertEqual(response.status_code, 302)

    def test_payer_and_recipient_can_access_payment(self):
        """
        Prueba que tanto el pagador como el receptor pueden acceder a sus pagos.
        """
        print("\nProbando acceso autorizado a pago...")

        # Login como pagador
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)

        # El pagador puede acceder al detalle
        response = self.client.get(
            reverse(URL_PAYMENT_DETAIL, args=[self.completed_payment.id])
        )
        self.assertEqual(response.status_code, 200)

        self.client.logout()

        # Login como receptor
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)

        # El receptor puede acceder al detalle
        response = self.client.get(
            reverse(URL_PAYMENT_DETAIL, args=[self.completed_payment.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_refund(self):
        """
        Prueba que solo el receptor puede reembolsar un pago.
        """
        print("\nProbando reembolso no autorizado...")

        # Login como pagador
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)

        # Intentar reembolsar
        response = self.client.post(
            reverse(URL_REFUND_PAYMENT, args=[self.completed_payment.id])
        )

        # Debe redireccionar (acceso denegado)
        self.assertEqual(response.status_code, 302)

        # El pago no debe estar reembolsado
        self.completed_payment.refresh_from_db()
        self.assertNotEqual(self.completed_payment.status, PAYMENT_STATUS_REFUNDED)

    def test_unauthorized_cancel(self):
        """
        Prueba que solo el pagador puede cancelar un pago pendiente.
        """
        print("\nProbando cancelación no autorizada...")

        # Login como receptor
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)

        # Intentar cancelar
        response = self.client.post(
            reverse(URL_CANCEL_PAYMENT, args=[self.pending_payment.id])
        )

        # Debe redireccionar (acceso denegado)
        self.assertEqual(response.status_code, 302)

        # El pago no debe estar cancelado
        self.pending_payment.refresh_from_db()
        self.assertNotEqual(self.pending_payment.status, PAYMENT_STATUS_CANCELLED)

    def test_cannot_cancel_completed_payment(self):
        """
        Prueba que no se puede cancelar un pago que ya está completado.
        """
        print("\nProbando cancelación de pago completado...")

        # Login como pagador
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)

        # Intentar cancelar un pago completado
        response = self.client.post(
            reverse(URL_CANCEL_PAYMENT, args=[self.completed_payment.id])
        )

        # Debe redireccionar
        self.assertEqual(response.status_code, 302)

        # El pago no debe estar cancelado
        self.completed_payment.refresh_from_db()
        self.assertNotEqual(self.completed_payment.status, PAYMENT_STATUS_CANCELLED)

    def test_cannot_refund_pending_payment(self):
        """
        Prueba que no se puede reembolsar un pago pendiente.
        """
        print("\nProbando reembolso de pago pendiente...")

        # Login como receptor
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)

        # Intentar reembolsar un pago pendiente
        response = self.client.post(
            reverse(URL_REFUND_PAYMENT, args=[self.pending_payment.id])
        )

        # Debe redireccionar
        self.assertEqual(response.status_code, 302)

        # El pago no debe estar reembolsado
        self.pending_payment.refresh_from_db()
        self.assertNotEqual(self.pending_payment.status, PAYMENT_STATUS_REFUNDED)

    @patch("payments._utils.create_checkout_session")
    def test_unauthorized_create_payment_own_ride(self, mock_checkout):
        """
        Prueba que un conductor no puede pagar su propio viaje.
        """
        print("\nProbando creación de pago para viaje propio...")

        # Login como conductor/receptor
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)

        # Intentar crear un pago para su propio viaje
        response = self.client.post(
            reverse(URL_CREATE_PAYMENT, args=[self.ride.id]),
            {"terms_accepted": "on"},
        )

        # Debe redireccionar
        self.assertEqual(response.status_code, 302)

        # No debe llamarse a la función de crear sesión de Stripe
        mock_checkout.assert_not_called()

    def test_csrf_protection_payment_operations(self):
        """
        Prueba que las operaciones de pago están protegidas contra CSRF.
        """
        print("\nProbando protección CSRF para operaciones de pago...")

        # Login como pagador
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)

        # Desactivar verificación CSRF para este cliente
        self.client.handler.enforce_csrf_checks = True

        # Intentar cancelar sin token CSRF
        response = self.client.post(
            reverse(URL_CANCEL_PAYMENT, args=[self.pending_payment.id])
        )

        # Debería fallar por falta de token CSRF
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Login como receptor y probar reembolso sin CSRF
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)
        response = self.client.post(
            reverse(URL_REFUND_PAYMENT, args=[self.completed_payment.id])
        )

        # Debería fallar por falta de token CSRF
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_nonexistent_payment(self):
        """
        Prueba acceder a un pago que no existe.
        """
        print("\nProbando acceso a pago inexistente...")

        # Login como pagador
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)

        # Intentar acceder a un pago con ID inexistente
        response = self.client.get(reverse(URL_PAYMENT_DETAIL, args=[99999]))

        # Debería dar error 404
        self.assertEqual(response.status_code, 404)

    @patch("payments._utils.create_checkout_session")
    def test_create_payment_full_ride(self, mock_checkout):
        """
        Prueba que no se puede crear un pago para un viaje lleno.
        """
        print("\nProbando creación de pago para viaje lleno...")

        # Crear un viaje con todos los asientos ocupados
        full_ride = Ride.objects.create(
            driver=self.recipient,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=self.future_date,
            price=RIDE_PRICE,
            total_seats=1,
        )
        full_ride.passengers.add(self.other_user)

        # Login como pagador
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)

        # Intentar crear un pago para el viaje lleno
        response = self.client.post(
            reverse(URL_CREATE_PAYMENT, args=[full_ride.id]),
            {"terms_accepted": "on"},
        )

        # Debe redireccionar
        self.assertEqual(response.status_code, 302)

        # No debe llamarse a la función de crear sesión de Stripe
        mock_checkout.assert_not_called()
