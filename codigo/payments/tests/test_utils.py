from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from payments.models import Payment
from rides.models import Ride
from payments import _utils
from payments.tests.test_constants import *

class PaymentUtilsTests(TestCase):
    """
    Pruebas para las funciones de utilidad del módulo de pagos.
    """
    
    def setUp(self):
        """
        Configura los datos iniciales para las pruebas.
        """
        print("\nConfigurando pruebas para las funciones de utilidad...")
        
        self.factory = RequestFactory()
        
        # Crear usuarios
        self.payer = User.objects.create_user(
            username=PAYER_USERNAME,
            email=PAYER_EMAIL,
            password=PAYER_PASSWORD
        )
        
        self.recipient = User.objects.create_user(
            username=RECIPIENT_USERNAME,
            email=RECIPIENT_EMAIL,
            password=RECIPIENT_PASSWORD
        )
        
        # Crear viaje
        self.future_date = timezone.now() + timedelta(days=RIDE_DAYS_FUTURE)
        self.ride = Ride.objects.create(
            driver=self.recipient,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=self.future_date,
            price=RIDE_PRICE,
            total_seats=4
        )
        
        # Crear pagos
        self.pending_payment = Payment.objects.create(
            payer=self.payer,
            recipient=self.recipient,
            amount=PAYMENT_AMOUNT,
            ride=self.ride,
            status=PAYMENT_STATUS_PENDING,
            payment_method=PAYMENT_METHOD_STRIPE,
            concept=PAYMENT_CONCEPT
        )
        
        self.completed_payment = Payment.objects.create(
            payer=self.payer,
            recipient=self.recipient,
            amount=PAYMENT_AMOUNT,
            ride=self.ride,
            status=PAYMENT_STATUS_COMPLETED,
            payment_method=PAYMENT_METHOD_CREDIT_CARD,
            concept=PAYMENT_CONCEPT,
            stripe_payment_intent_id=PAYMENT_STRIPE_ID
        )
        
        print(f"Creados {Payment.objects.count()} pagos para pruebas de utilidades.")
    
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_create):
        """
        Prueba la función create_checkout_session.
        """
        print("\nProbando create_checkout_session...")
        
        # Configurar el mock
        mock_session = MagicMock()
        mock_session.id = "test_checkout_session_id"
        mock_session.url = "https://checkout.stripe.com/test-session"
        mock_create.return_value = mock_session
        
        # Crear una request simulada con un objeto Mock
        request = MagicMock()
        request.scheme = 'http'
        request.get_host.return_value = 'testserver'
        
        # Llamar a la función
        url = _utils.create_checkout_session(self.pending_payment, request)
        
        # Verificar resultados
        self.assertEqual(url, "https://checkout.stripe.com/test-session")
        mock_create.assert_called_once()
        
        # Verificar que el ID de la sesión se guardó en el pago
        self.pending_payment.refresh_from_db()
        self.assertEqual(self.pending_payment.stripe_payment_intent_id, "test_checkout_session_id")
    
    @patch('stripe.checkout.Session.retrieve')
    @patch('stripe.PaymentIntent.retrieve')
    def test_get_payment_status(self, mock_pi_retrieve, mock_session_retrieve):
        """
        Prueba la función get_payment_status.
        """
        print("\nProbando get_payment_status...")
        
        # Configurar los mocks
        mock_session = MagicMock()
        mock_session.payment_intent = "pi_test_12345"
        mock_session_retrieve.return_value = mock_session
        
        mock_payment_intent = MagicMock()
        mock_payment_intent.status = "succeeded"
        mock_pi_retrieve.return_value = mock_payment_intent
        
        # Llamar a la función
        status = _utils.get_payment_status("test_session_id")
        
        # Verificar resultados
        self.assertEqual(status, "succeeded")
        mock_session_retrieve.assert_called_once_with("test_session_id")
        mock_pi_retrieve.assert_called_once_with("pi_test_12345")
    
    @patch('stripe.checkout.Session.retrieve')
    @patch('stripe.Refund.create')
    def test_process_refund(self, mock_refund_create, mock_session_retrieve):
        """
        Prueba la función process_refund.
        """
        print("\nProbando process_refund...")
        
        # Configurar los mocks
        mock_session = MagicMock()
        mock_session.payment_intent = "pi_test_12345"
        mock_session_retrieve.return_value = mock_session
        
        mock_refund = MagicMock()
        mock_refund.id = "re_test_12345"
        mock_refund_create.return_value = mock_refund
        
        # Llamar a la función
        success, result = _utils.process_refund(self.completed_payment)
        
        # Verificar resultados
        self.assertTrue(success)
        self.assertEqual(result, "re_test_12345")
        mock_session_retrieve.assert_called_once_with(PAYMENT_STRIPE_ID)
        mock_refund_create.assert_called_once_with(
            payment_intent="pi_test_12345",
            reason="requested_by_customer"
        )
    
    def test_validate_payment_access(self):
        """
        Prueba la función validate_payment_access.
        """
        print("\nProbando validate_payment_access...")
        
        # El pagador tiene acceso
        self.assertTrue(_utils.validate_payment_access(self.pending_payment, self.payer))
        
        # El receptor tiene acceso
        self.assertTrue(_utils.validate_payment_access(self.pending_payment, self.recipient))
        
        # Un tercero no tiene acceso
        other_user = User.objects.create_user("otro", "otro@example.com", "password123")
        self.assertFalse(_utils.validate_payment_access(self.pending_payment, other_user))
    
    def test_validate_refund_permission(self):
        """
        Prueba la función validate_refund_permission.
        """
        print("\nProbando validate_refund_permission...")
        
        # El receptor puede reembolsar un pago completado
        has_perm, _ = _utils.validate_refund_permission(self.completed_payment, self.recipient)
        self.assertTrue(has_perm)
        
        # El pagador no puede reembolsar
        has_perm, error_msg = _utils.validate_refund_permission(self.completed_payment, self.payer)
        self.assertFalse(has_perm)
        self.assertEqual(error_msg, ERROR_REFUND_PERMISSION)
        
        # Nadie puede reembolsar un pago pendiente
        has_perm, error_msg = _utils.validate_refund_permission(self.pending_payment, self.recipient)
        self.assertFalse(has_perm)
        self.assertEqual(error_msg, ERROR_ONLY_COMPLETED)
    
    def test_validate_cancel_permission(self):
        """
        Prueba la función validate_cancel_permission.
        """
        print("\nProbando validate_cancel_permission...")
        
        # El pagador puede cancelar un pago pendiente
        has_perm, _ = _utils.validate_cancel_permission(self.pending_payment, self.payer)
        self.assertTrue(has_perm)
        
        # El receptor no puede cancelar
        has_perm, error_msg = _utils.validate_cancel_permission(self.pending_payment, self.recipient)
        self.assertFalse(has_perm)
        self.assertEqual(error_msg, ERROR_CANCEL_PERMISSION)
        
        # Nadie puede cancelar un pago completado
        has_perm, error_msg = _utils.validate_cancel_permission(self.completed_payment, self.payer)
        self.assertFalse(has_perm)
        self.assertEqual(error_msg, ERROR_ONLY_PENDING)
    
    def test_format_payment_description(self):
        """
        Prueba la función format_payment_description.
        """
        print("\nProbando format_payment_description...")
        
        # Pago con viaje
        description = _utils.format_payment_description(self.pending_payment)
        expected = f"Pago de viaje: {RIDE_ORIGIN} → {RIDE_DESTINATION}"
        self.assertEqual(description, expected)
        
        # Pago sin viaje
        payment_without_ride = Payment(id=999)
        description = _utils.format_payment_description(payment_without_ride)
        expected = f"Pago #999"
        self.assertEqual(description, expected)
