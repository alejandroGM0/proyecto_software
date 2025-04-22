# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================

"""
Pruebas para las vistas del dashboard.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from rides.models import Ride
from reports.models import Report
from accounts.models import UserProfile
from chat.models import Chat, Message
from dashboard.views import is_admin
from dashboard.tests.test_constants import *

class DashboardViewsTests(TestCase):
    """Pruebas para las vistas de dashboard."""
    
    def setUp(self):
        """Configura los datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para las vistas del dashboard...")
        
        self.client = Client()
        
        self.admin_user = User.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD
        )
        UserProfile.objects.create(user=self.admin_user)
        
        self.regular_user = User.objects.create_user(
            username=REGULAR_USERNAME,
            email=REGULAR_EMAIL,
            password=REGULAR_PASSWORD
        )
        UserProfile.objects.create(user=self.regular_user)
        
        
        self.future_date = timezone.now() + timedelta(days=DAYS_FUTURE)
        
        self.ride = Ride.objects.create(
            driver=self.regular_user,
            origin=TEST_ORIGIN,
            destination=TEST_DESTINATION,
            departure_time=self.future_date,
            total_seats=TEST_SEATS,
            price=TEST_PRICE
        )
        
        
        self.report = Report.objects.create(
            title="Test Report",
            description="Test Description",
            user=self.regular_user,
            report_type="system"
        )
        
        print("Se han creado los datos para las pruebas de vistas del dashboard.")
    
    def test_is_admin_function(self):
        """Prueba la función que verifica si un usuario es administrador."""
        print("\nProbando función is_admin...")
        
        self.assertTrue(is_admin(self.admin_user))
        self.assertFalse(is_admin(self.regular_user))
    
    def test_dashboard_view_access_unauthorized(self):
        """Prueba que un usuario no autorizado no puede acceder al dashboard."""
        print("\nProbando acceso no autorizado al dashboard...")
        
        
        response = self.client.get(reverse(URL_DASHBOARD))
        self.assertEqual(response.status_code, 302)  
        
        
        self.client.login(username=REGULAR_USERNAME, password=REGULAR_PASSWORD)
        response = self.client.get(reverse(URL_DASHBOARD))
        self.assertEqual(response.status_code, 302)  
    
    def test_dashboard_view_access_authorized(self):
        """Prueba que un admin puede acceder al dashboard."""
        print("\nProbando acceso autorizado al dashboard...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_DASHBOARD))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_DASHBOARD)
    
    def test_dashboard_view_with_period_param(self):
        """Prueba acceder al dashboard con un período específico."""
        print("\nProbando dashboard con parámetro de período...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_DASHBOARD) + "?period=week")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('time_period', response.context)
        self.assertEqual(response.context['time_period'], 'week')
    
    def test_ride_management_view(self):
        """Prueba la vista de gestión de viajes."""
        print("\nProbando vista de gestión de viajes...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_RIDE_MANAGEMENT))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_RIDE_MANAGEMENT)
        
        
        self.assertIn('rides', response.context)
        
        
        self.assertIn(self.ride, response.context['rides'])
    
    def test_ride_management_view_with_filters(self):
        """Prueba la vista de gestión de viajes con filtros."""
        print("\nProbando vista de gestión de viajes con filtros...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        
        
        response = self.client.get(reverse(URL_RIDE_MANAGEMENT) + f"?origin={TEST_ORIGIN}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ride, response.context['rides'])
        
        
        response = self.client.get(reverse(URL_RIDE_MANAGEMENT) + f"?destination={TEST_DESTINATION}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ride, response.context['rides'])
        
        
        response = self.client.get(reverse(URL_RIDE_MANAGEMENT) + "?search=noexiste")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rides']), 0)
    
    def test_user_management_view(self):
        """Prueba la vista de gestión de usuarios."""
        print("\nProbando vista de gestión de usuarios...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_USER_MANAGEMENT))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_USER_MANAGEMENT)
        
        
        self.assertIn('users', response.context)
    
    def test_chat_management_view(self):
        """Prueba la vista de gestión de chats."""
        print("\nProbando vista de gestión de chats...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_CHAT_MANAGEMENT))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_CHAT_MANAGEMENT)
        
        
        self.assertIn('chats', response.context)
    
    def test_trip_stats_view(self):
        """Prueba la vista de estadísticas de viajes."""
        print("\nProbando vista de estadísticas de viajes...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_TRIP_STATS))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_TRIP_STATS)
        
        
        self.assertIn('trip_data', response.context)
        self.assertIn('time_period', response.context)
        self.assertIn('trip_data_json', response.context)
    
    def test_message_stats_view(self):
        """Prueba la vista de estadísticas de mensajes."""
        print("\nProbando vista de estadísticas de mensajes...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_MSG_STATS))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_MSG_STATS)
        
        
        self.assertIn('msg_data', response.context)
        self.assertIn('time_period', response.context)
        self.assertIn('msg_data_json', response.context)
    
    def test_report_stats_view(self):
        """Prueba la vista de estadísticas de reportes."""
        print("\nProbando vista de estadísticas de reportes...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_REPORT_STATS))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_REPORT_STATS)
        
        
        self.assertIn('report_data', response.context)
        self.assertIn('time_period', response.context)
        self.assertIn('report_data_json', response.context)
    
    def test_user_stats_view(self):
        """Prueba la vista de estadísticas de usuarios."""
        print("\nProbando vista de estadísticas de usuarios...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse(URL_USER_STATS))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_USER_STATS)
        
        
        self.assertIn('user_data', response.context)
        self.assertIn('payment_data', response.context)
        self.assertIn('time_period', response.context)
        self.assertIn('user_data_json', response.context)
        self.assertIn('payment_data_json', response.context)
    
    def test_get_trip_data_json(self):
        """Prueba el API JSON para datos de viajes."""
        print("\nProbando API JSON para datos de viajes...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse('dashboard:get_trip_data_json'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('active_rides', data)
        self.assertIn('completed_rides', data)
        self.assertIn('total_rides', data)
    
    def test_get_message_data_json(self):
        """Prueba el API JSON para datos de mensajes."""
        print("\nProbando API JSON para datos de mensajes...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse('dashboard:get_message_data_json'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        
        data = response.json()
        self.assertIn('total', data)
        self.assertIn('labels', data)
        self.assertIn('data', data)
    
    def test_get_report_data_json(self):
        """Prueba el API JSON para datos de reportes."""
        print("\nProbando API JSON para datos de reportes...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse('dashboard:get_report_data_json'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        
        data = response.json()
        self.assertIn('total', data)
        self.assertIn('unread', data)
        self.assertIn('resolved', data)
    
    def test_get_user_data_json(self):
        """Prueba el API JSON para datos de usuarios."""
        print("\nProbando API JSON para datos de usuarios...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse('dashboard:get_user_data_json'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        
        data = response.json()
        self.assertIn('total', data)
        self.assertIn('active', data)
        self.assertIn('inactive', data)
    
    def test_get_payment_data_json(self):
        """Prueba el API JSON para datos de pagos."""
        print("\nProbando API JSON para datos de pagos...")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse('dashboard:get_payment_data_json'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        
        data = response.json()
        self.assertIn('total', data)
        self.assertIn('amount', data)
        self.assertIn('avg_per_transaction', data)
    
    def test_get_chat_messages(self):
        """Prueba la obtención de mensajes de chat."""
        print("\nProbando obtención de mensajes de chat...")
        
        
        chat = Chat.objects.create()
        chat.participants.add(self.admin_user, self.regular_user)
        
        
        Message.objects.create(chat=chat, sender=self.admin_user, content="Mensaje de prueba 1")
        Message.objects.create(chat=chat, sender=self.regular_user, content="Mensaje de prueba 2")
        
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse('dashboard:get_chat_messages', args=[chat.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        
        data = response.json()
        self.assertIn('messages', data)
        self.assertIn('participants', data)
        
        
        self.assertEqual(len(data['messages']), 2)