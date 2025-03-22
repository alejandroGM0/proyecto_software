from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

from chat.models import Message
from rides.models import Ride
from .test_constants import *

class ChatViewsTests(TestCase):
    """Pruebas para las vistas de chat"""

    def setUp(self):
        self.client = Client()
        
        self.driver = User.objects.create_user(
            username=DRIVER_USERNAME,
            email=DRIVER_EMAIL,
            password=DRIVER_PASSWORD
        )

        self.passenger = User.objects.create_user(
            username=PASSENGER_USERNAME,
            email=PASSENGER_EMAIL,
            password=PASSENGER_PASSWORD
        )
        
        self.other_user = User.objects.create_user(
            username=OTHER_USERNAME,
            email=OTHER_EMAIL,
            password=OTHER_PASSWORD
        )

        self.future_date = timezone.now() + timedelta(days=RIDE_DAYS_IN_FUTURE)
        self.ride = Ride.objects.create(
            driver=self.driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=self.future_date,
            total_seats=RIDE_TOTAL_SEATS,
            price=RIDE_PRICE
        )
        
        self.ride.passengers.add(self.passenger)
        
        Message.objects.create(
            ride=self.ride,
            sender=self.driver,
            content=DRIVER_MESSAGE,
            is_read=True
        )
        
        Message.objects.create(
            ride=self.ride,
            sender=self.passenger,
            content=PASSENGER_MESSAGE,
            is_read=False
        )

    def test_ride_chat_view_requires_login(self):
        """Prueba que la vista de chat requiere login"""
        response = self.client.get(reverse(URL_RIDE_CHAT, args=[self.ride.id]))
        self.assertEqual(response.status_code, 302) 

    def test_ride_chat_view_without_ride_id(self):
        """Prueba la vista de chat sin ID de viaje inicial pero listando chats"""
        self.client.login(username=DRIVER_USERNAME, password=DRIVER_PASSWORD)
        response = self.client.get(reverse(URL_RIDE_CHAT, args=[self.ride.id]))
        
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, TEMPLATE_CHAT)
        self.assertIn(CONTEXT_CHATS_DATA, response.context)
        self.assertIn(CONTEXT_SELECTED_RIDE, response.context)

    def test_ride_chat_view_with_ride_id(self):
        """Prueba la vista de chat con un ID de viaje válido"""
        self.client.login(username=DRIVER_USERNAME, password=DRIVER_PASSWORD)
        response = self.client.get(reverse(URL_RIDE_CHAT, args=[self.ride.id]))
        
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, TEMPLATE_CHAT)
        self.assertIn(CONTEXT_CHATS_DATA, response.context)
        self.assertIn(CONTEXT_SELECTED_RIDE, response.context)
        self.assertEqual(response.context[CONTEXT_SELECTED_RIDE], self.ride)
        
    def test_get_messages_view(self):
        """Prueba la vista para obtener mensajes"""
        self.client.login(username=DRIVER_USERNAME, password=DRIVER_PASSWORD)
        response = self.client.get(reverse(URL_GET_MESSAGES, args=[self.ride.id]))
        
        self.assertEqual(response.status_code, 200) 
        data = json.loads(response.content)
        
        self.assertIn('messages', data)
        self.assertIn('is_active', data)
        self.assertEqual(len(data['messages']), 2)
        
        message_contents = [msg['content'] for msg in data['messages']]
        self.assertIn(DRIVER_MESSAGE, message_contents)
        self.assertIn(PASSENGER_MESSAGE, message_contents)
        
    def test_get_messages_view_unauthorized(self):
        """Prueba que un usuario no autorizado no puede acceder a los mensajes"""
        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)
        response = self.client.get(reverse(URL_GET_MESSAGES, args=[self.ride.id]))
        
        self.assertEqual(response.status_code, 403)