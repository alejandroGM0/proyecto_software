# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from chat.models import Message
from rides.models import Ride
from .test_constants import *

class MessageModelTests(TestCase):

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

        self.future_date = timezone.now() + timedelta(days=RIDE_DAYS_IN_FUTURE)
        self.ride = Ride.objects.create(
            driver=self.driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=self.future_date,
            total_seats=RIDE_TOTAL_SEATS,
            price=RIDE_PRICE
        )
        self.ride.refresh_from_db()
        if not hasattr(self.ride, 'chat') or self.ride.chat is None:
            from chat.models import Chat
            chat = Chat.objects.create()
            self.ride.chat = chat
            self.ride.save()
        self.ride.refresh_from_db()
        self.ride.passengers.add(self.passenger)

    def test_message_creation(self):
        """Prueba la creación de mensajes"""
        chat = self.ride.chat
        message = Message.objects.create(
            chat=chat,
            sender=self.driver,
            content=DRIVER_MESSAGE,
            is_read=False
        )
        self.assertEqual(message.chat, chat)
        self.assertEqual(message.sender, self.driver)
        self.assertEqual(message.content, DRIVER_MESSAGE)
        self.assertFalse(message.is_read)
        self.assertIsNotNone(message.created_at)

    def test_message_string_representation(self):
        """Prueba la representación en cadena del mensaje"""
        chat = self.ride.chat
        message = Message.objects.create(
            chat=chat,
            sender=self.driver,
            content=DRIVER_MESSAGE,
            is_read=False
        )
        expected = DRIVER_MESSAGE
        self.assertEqual(str(message), expected)