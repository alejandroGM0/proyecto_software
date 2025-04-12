# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from rides.models import Ride
from chat.models import Message
from rides.tests.test_constants import *


class ChatRideIntegrationTests(TestCase):
    def setUp(self):
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

        self.future_date = timezone.now() + timedelta(days=FUTURE_DAYS)
        self.ride = Ride.objects.create(
            driver=self.driver,
            origin=ORIGIN_CITY,
            destination=DESTINATION_CITY,
            departure_time=self.future_date,
            total_seats=DEFAULT_SEATS,
            price=DEFAULT_PRICE
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

        self.client = Client()

    def test_ride_chat_access_as_driver(self):
        """Prueba acceso al chat como conductor"""
        self.client.login(username=DRIVER_USERNAME, password=DRIVER_PASSWORD)
        response = self.client.get(reverse('chat:ride_chat', args=[self.ride.id]))
        self.assertEqual(response.status_code, 200)

    def test_ride_chat_access_as_passenger(self):
        """Prueba acceso al chat como pasajero"""
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        response = self.client.get(reverse('chat:ride_chat', args=[self.ride.id]))
        self.assertEqual(response.status_code, 200)

    def test_ride_chat_access_unauthorized(self):
        """Prueba que un usuario no relacionado con el viaje no puede acceder al chat"""
        otro_usuario = User.objects.create_user(
            username=OTHER_USERNAME,
            email=OTHER_EMAIL,
            password=OTHER_PASSWORD
        )

        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)
        response = self.client.get(reverse('chat:ride_chat', args=[self.ride.id]))

        self.assertEqual(response.status_code, 302)

    def test_get_messages_api(self):
        """Prueba el API para obtener mensajes del chat"""
        self.client.login(username=DRIVER_USERNAME, password=DRIVER_PASSWORD)
        response = self.client.get(reverse('chat:get_messages', args=[self.ride.id]))

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('messages', data)
        self.assertIn('is_active', data)
        self.assertEqual(len(data['messages']), 2)

        message_contents = [msg['content'] for msg in data['messages']]
        self.assertIn(DRIVER_MESSAGE, message_contents)
        self.assertIn(PASSENGER_MESSAGE, message_contents)