from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from payments.models import Payment
from rides.models import Ride
from payments.tests.test_constants import *
from payments.constants import ERROR_PAYMENT_PROCESSING, PAYMENT_STATUS_COMPLETED, PAYMENT_STATUS_PENDING
from accounts.models import UserProfile

class PaymentViewsTests(TestCase):
    """
    Pruebas para las vistas de pagos.
    """
    
    def setUp(self):
        """
        Configura los datos iniciales para las pruebas.
        """
        print("\nConfigurando pruebas para las vistas de pagos...")
        
        self.client = Client()
        
        # Crear usuarios
        self.payer = User.objects.create_user(
            username=PAYER_USERNAME,
            email=PAYER_EMAIL,
            password=PAYER_PASSWORD
        )
        UserProfile.objects.create(user=self.payer)
        
        self.recipient = User.objects.create_user(
            username=RECIPIENT_USERNAME,
            email=RECIPIENT_EMAIL,
            password=RECIPIENT_PASSWORD
        )
        UserProfile.objects.create(user=self.recipient)
        
        self.admin_user = User.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD
        )
        UserProfile.objects.create(user=self.admin_user)
        
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
        
        print(f"Creados {Payment.objects.count()} pagos para pruebas de vistas.")
    
    def test_payment_list_view(self):
        """
        Prueba que la vista de lista de pagos funciona correctamente.
        """
        print("\nProbando vista de lista de pagos...")
        
        # Sin autenticación debe redirigir a login
        response = self.client.get(reverse(URL_PAYMENT_LIST))
        self.assertEqual(response.status_code, 302)
        
        # Con autenticación como pagador
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        response = self.client.get(reverse(URL_PAYMENT_LIST))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_PAYMENT_LIST)
        
        # El pagador debe ver sus pagos realizados
        self.assertEqual(len(response.context['payments_made']), 2)
        self.assertEqual(len(response.context['payments_received']), 0)
        
        # Ahora como receptor
        self.client.logout()
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)
        response = self.client.get(reverse(URL_PAYMENT_LIST))
        
        self.assertEqual(response.status_code, 200)
        # El receptor debe ver los pagos recibidos
        self.assertEqual(len(response.context['payments_made']), 0)
        self.assertEqual(len(response.context['payments_received']), 2)
    
    def test_payment_history_view(self):
        """
        Prueba que la vista de historial de pagos funciona correctamente.
        """
        print("\nProbando vista de historial de pagos...")
        
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        response = self.client.get(reverse(URL_PAYMENT_HISTORY))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_PAYMENT_HISTORY)
        
        # Debe mostrar todos los pagos del usuario (como pagador o receptor)
        self.assertEqual(len(response.context['payments']), 2)
        
        # Filtrado por estado
        response = self.client.get(reverse(URL_PAYMENT_HISTORY) + f"?status={PAYMENT_STATUS_COMPLETED}")
        self.assertEqual(len(response.context['payments']), 1)
    
    def test_payment_detail_view(self):
        """
        Prueba que la vista de detalle de pago funciona correctamente.
        """
        print("\nProbando vista de detalle de pago...")
        
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        response = self.client.get(reverse(URL_PAYMENT_DETAIL, args=[self.completed_payment.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_PAYMENT_DETAIL)
        self.assertEqual(response.context['payment'], self.completed_payment)
    
    def test_payment_detail_view_unauthorized(self):
        """
        Prueba que no se puede acceder al detalle de un pago sin autorización.
        """
        print("\nProbando restricción de acceso a detalle de pago...")
        
        # Crear un tercer usuario que no tiene relación con el pago
        other_user = User.objects.create_user('otro', 'otro@example.com', 'contraseña123')
        UserProfile.objects.create(user=other_user)
        self.client.login(username='otro', password='contraseña123')
        
        response = self.client.get(reverse(URL_PAYMENT_DETAIL, args=[self.completed_payment.id]))
        
        # Debe redirigir a la lista de pagos
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse(URL_PAYMENT_LIST)))
    
    @patch('payments._utils.create_checkout_session')
    def test_create_payment_view(self, mock_create_checkout):
        """
        Prueba la creación de un pago.
        """
        print("\nProbando creación de pago...")
        
        # Simular respuesta exitosa de Stripe
        mock_create_checkout.return_value = "https://checkout.stripe.com/test-session"
        
        # Iniciar sesión como tercer usuario (que no es ni pagador ni receptor en los pagos existentes)
        other_user = User.objects.create_user('nuevo', 'nuevo@example.com', 'contraseña123')
        UserProfile.objects.create(user=other_user)
        self.client.login(username='nuevo', password='contraseña123')
        
        # Intentar pagar un viaje
        form_data = {
            'terms_accepted': 'on'
        }
        
        response = self.client.post(
            reverse(URL_CREATE_PAYMENT, args=[self.ride.id]),
            form_data
        )
        
        # Debe redireccionar a Stripe
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://checkout.stripe.com/test-session")
        
        # Verificar que el pago se creó
        self.assertEqual(Payment.objects.count(), 3)
        new_payment = Payment.objects.filter(payer=other_user).first()
        self.assertIsNotNone(new_payment)
        self.assertEqual(new_payment.status, PAYMENT_STATUS_PENDING)
    
    def test_create_payment_own_ride(self):
        """
        Prueba que un conductor no puede pagar su propio viaje.
        """
        print("\nProbando restricción de pago del propio viaje...")
        
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)
        response = self.client.get(reverse(URL_CREATE_PAYMENT, args=[self.ride.id]))
        
        # Debe redirigir al detalle del viaje
        self.assertEqual(response.status_code, 302)
    
    def test_payment_success_view(self):
        """
        Prueba la vista de éxito de pago.
        """
        print("\nProbando vista de éxito de pago...")
        
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        
        with patch('payments._utils.get_payment_status') as mock_get_status:
            mock_get_status.return_value = 'succeeded'
            
            response = self.client.get(
                reverse(URL_PAYMENT_SUCCESS, args=[self.pending_payment.id]) + "?session_id=test_session"
            )
            
            self.assertEqual(response.status_code, 302)
            
            # Verificar que el estado del pago cambió a completado
            self.pending_payment.refresh_from_db()
            self.assertEqual(self.pending_payment.status, PAYMENT_STATUS_COMPLETED)
    
    def test_refund_payment_view(self):
        """
        Prueba la vista de reembolso de pago.
        """
        print("\nProbando vista de reembolso de pago...")
        
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)
        
        # Primero GET para mostrar la confirmación
        response = self.client.get(reverse(URL_REFUND_PAYMENT, args=[self.completed_payment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_REFUND_PAYMENT)
        
        # Ahora POST para confirmar
        with patch('payments._utils.process_refund') as mock_refund:
            mock_refund.return_value = (True, "refund_test_id")
            
            response = self.client.post(reverse(URL_REFUND_PAYMENT, args=[self.completed_payment.id]))
            self.assertEqual(response.status_code, 302)
            
            # Verificar que el estado del pago cambió a reembolsado
            self.completed_payment.refresh_from_db()
            self.assertEqual(self.completed_payment.status, PAYMENT_STATUS_REFUNDED)
            self.assertEqual(self.completed_payment.stripe_refund_id, "refund_test_id")
    
    def test_refund_payment_unauthorized(self):
        """
        Prueba que solo el receptor puede reembolsar un pago.
        """
        print("\nProbando restricción de reembolso...")
        
        # El pagador intenta reembolsar
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        response = self.client.post(reverse(URL_REFUND_PAYMENT, args=[self.completed_payment.id]))
        
        # No debe permitir reembolso
        self.assertEqual(response.status_code, 302)
        self.completed_payment.refresh_from_db()
        self.assertEqual(self.completed_payment.status, PAYMENT_STATUS_COMPLETED)
    
    def test_cancel_payment_view(self):
        """
        Prueba la cancelación de un pago pendiente.
        """
        print("\nProbando cancelación de pago...")
        
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        response = self.client.post(reverse(URL_CANCEL_PAYMENT, args=[self.pending_payment.id]))
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el pago se canceló
        self.pending_payment.refresh_from_db()
        self.assertEqual(self.pending_payment.status, PAYMENT_STATUS_CANCELLED)
    
    def test_cancel_payment_unauthorized(self):
        """
        Prueba que solo el pagador puede cancelar un pago.
        """
        print("\nProbando restricción de cancelación...")
        
        # El receptor intenta cancelar
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)
        response = self.client.post(reverse(URL_CANCEL_PAYMENT, args=[self.pending_payment.id]))
        
        # No debe permitir cancelación
        self.assertEqual(response.status_code, 302)
        self.pending_payment.refresh_from_db()
        self.assertEqual(self.pending_payment.status, PAYMENT_STATUS_PENDING)
    
    @patch('payments._utils.create_checkout_session')
    def test_create_payment_invalid_form(self, mock_create_checkout):
        """
        Prueba que no se crea un pago si el formulario es inválido.
        """
        print("\nProbando creación de pago con formulario inválido...")
        
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        
        # Enviar formulario sin aceptar términos
        form_data = {}
        response = self.client.post(reverse(URL_CREATE_PAYMENT, args=[self.ride.id]), form_data)
        
        # Puede ser 200 o 302 según la implementación
        self.assertIn(response.status_code, [200, 302])
        
        if response.status_code == 200:
            self.assertTemplateUsed(response, TEMPLATE_CREATE_PAYMENT)
            self.assertFalse(response.context['form'].is_valid())
            
        # Verificar que no se creó un nuevo pago
        self.assertEqual(Payment.objects.count(), 2)  # Los dos pagos iniciales
    
    def test_create_payment_full_ride(self):
        """
        Prueba crear un pago para un viaje que ya está lleno.
        """
        print("\nProbando pago para viaje lleno...")
        
        # Crear un viaje sin asientos disponibles
        full_ride = Ride.objects.create(
            driver=self.recipient,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=self.future_date,
            price=RIDE_PRICE,
            total_seats=1,
        )
        
        # Añadir un pasajero para que esté lleno
        other_user = User.objects.create_user('another', 'another@example.com', 'contraseña123')
        UserProfile.objects.create(user=other_user)
        full_ride.passengers.add(other_user)
        
        # Verificar si el modelo tiene la propiedad seats_available
        if not hasattr(full_ride, 'seats_available'):
            setattr(full_ride.__class__, 'seats_available', property(lambda self: self.total_seats - self.passengers.count()))
        
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        response = self.client.get(reverse(URL_CREATE_PAYMENT, args=[full_ride.id]))
        
        # Debería redirigir con un mensaje de error
        self.assertEqual(response.status_code, 302)
    
    @patch('payments._utils.create_checkout_session')
    def test_create_payment_stripe_error(self, mock_create_checkout):
        """
        Prueba manejar errores al crear una sesión de Stripe.
        """
        print("\nProbando manejo de errores de Stripe...")
        
        # Simular error de Stripe
        mock_create_checkout.return_value = None
        
        # Usamos un usuario diferente para no tener pagos existentes
        other_user = User.objects.create_user('nuevo_error', 'nuevo_error@example.com', 'contraseña123')
        UserProfile.objects.create(user=other_user)
        
        # Contar pagos antes
        payment_count_before = Payment.objects.count()
        
        # Enviar formulario válido
        form_data = {'terms_accepted': 'on'}
        response = self.client.post(reverse(URL_CREATE_PAYMENT, args=[self.ride.id]), form_data)
        
        # Verificar que hay exactamente un pago más (en estado fallido)
        self.assertEqual(Payment.objects.count(), payment_count_before + 1)
        
        # El nuevo pago debe estar en estado fallido
        new_payment = Payment.objects.latest('id')
        self.assertEqual(new_payment.status, PAYMENT_STATUS_FAILED)
        
        # Debería mostrar un mensaje de error
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(ERROR_PAYMENT_PROCESSING in str(msg) for msg in messages))
    
    def test_payment_success_view_no_session(self):
        """
        Prueba la vista de éxito cuando no hay ID de sesión.
        """
        print("\nProbando vista de éxito sin ID de sesión...")
        
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        
        # Llamar sin session_id en la URL
        response = self.client.get(reverse(URL_PAYMENT_SUCCESS, args=[self.pending_payment.id]))
        
        self.assertEqual(response.status_code, 302)
        
        # El estado del pago no debería cambiar
        self.pending_payment.refresh_from_db()
        self.assertEqual(self.pending_payment.status, PAYMENT_STATUS_PENDING)
    
    def test_payment_cancel_view(self):
        """
        Prueba la vista de cancelación de pago (redirección desde Stripe).
        """
        print("\nProbando vista de cancelación desde Stripe...")
        
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        
        response = self.client.get(reverse(URL_PAYMENT_CANCEL, args=[self.pending_payment.id]))
        
        # Debe redirigir a la lista de pagos
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse(URL_PAYMENT_LIST)))
        
        # Verificar que el pago se canceló
        self.pending_payment.refresh_from_db()
        self.assertEqual(self.pending_payment.status, PAYMENT_STATUS_CANCELLED)
    
    def test_payment_cancel_completed_payment(self):
        """
        Prueba que no se puede cancelar un pago ya completado desde la redirección de Stripe.
        """
        print("\nProbando cancelación de pago completado desde Stripe...")
        
        self.client.login(username=PAYER_USERNAME, password=PAYER_PASSWORD)
        
        response = self.client.get(reverse(URL_PAYMENT_CANCEL, args=[self.completed_payment.id]))
        
        # Debe redirigir a la lista de pagos
        self.assertEqual(response.status_code, 302)
        
        # El estado del pago no debería cambiar
        self.completed_payment.refresh_from_db()
        self.assertEqual(self.completed_payment.status, PAYMENT_STATUS_COMPLETED)
    
    @patch('payments._utils.process_refund')
    def test_refund_payment_error(self, mock_refund):
        """
        Prueba manejar errores al procesar un reembolso.
        """
        print("\nProbando manejo de errores de reembolso...")
        
        # Simular error de reembolso
        mock_refund.return_value = (False, "Error de prueba en el reembolso")
        
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)
        
        response = self.client.post(reverse(URL_REFUND_PAYMENT, args=[self.completed_payment.id]))
        
        # Debería mostrar de nuevo la página de reembolso con un mensaje de error
        self.assertEqual(response.status_code, 200)
        
        # El estado del pago no debería cambiar
        self.completed_payment.refresh_from_db()
        self.assertEqual(self.completed_payment.status, PAYMENT_STATUS_COMPLETED)
    
    def test_refund_payment_wrong_status(self):
        """
        Prueba intentar reembolsar un pago que no está completado.
        """
        print("\nProbando reembolso de pago no completado...")
        
        self.client.login(username=RECIPIENT_USERNAME, password=RECIPIENT_PASSWORD)
        
        response = self.client.post(reverse(URL_REFUND_PAYMENT, args=[self.pending_payment.id]))
        
        # Debe redirigir al detalle con error
        self.assertEqual(response.status_code, 302)
        
        # El estado del pago no debería cambiar
        self.pending_payment.refresh_from_db()
        self.assertEqual(self.pending_payment.status, PAYMENT_STATUS_PENDING)


class ReservaConPagoStripeTests(TestCase):
    """
    Pruebas para el flujo de reserva con pago y Stripe.
    """
    def setUp(self):
        self.payer = User.objects.create_user('pagador', 'pagador@example.com', 'testpass')
        UserProfile.objects.create(user=self.payer)
        self.driver = User.objects.create_user('conductor', 'conductor@example.com', 'testpass')
        UserProfile.objects.create(user=self.driver)
        self.ride = Ride.objects.create(
            driver=self.driver,
            origin='Madrid',
            destination='Barcelona',
            departure_time=timezone.now() + timezone.timedelta(days=2),
            price=25.0,
            total_seats=2
        )
        self.client.login(username='pagador', password='testpass')

    @patch('payments._utils.create_checkout_session')
    def test_reserva_redirige_a_pago(self, mock_checkout):
        mock_checkout.return_value = 'https://checkout.stripe.com/test-session'
        response = self.client.post(reverse('payments:create_payment', args=[self.ride.id]), {'terms_accepted': 'on'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://checkout.stripe.com/test-session')
        self.ride.refresh_from_db()
        self.assertNotIn(self.payer, self.ride.passengers.all())

    @patch('payments._utils.get_payment_status')
    def test_usuario_se_añade_tras_pago(self, mock_status):
        # Simular pago completado
        mock_status.return_value = 'succeeded'
        payment = Payment.objects.create(
            payer=self.payer,
            recipient=self.driver,
            amount=self.ride.price,
            ride=self.ride,
            status=PAYMENT_STATUS_PENDING
        )
        url = reverse('payments:payment_success', args=[payment.id]) + '?session_id=testsession'
        response = self.client.get(url)
        self.ride.refresh_from_db()
        self.assertIn(self.payer, self.ride.passengers.all())
