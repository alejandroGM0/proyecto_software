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
from chat.public import user_has_chat_access, get_user_chats
from chat._utils import format_message_for_api, can_send_message
from .test_constants import *

class ChatUtilsTests(TestCase):

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
        self.ride.refresh_from_db()
        chat = self.ride.chat
        chat.participants.add(self.passenger)  # Asegura que el pasajero está en el chat
        Message.objects.create(
            chat=chat,
            sender=self.driver,
            content=DRIVER_MESSAGE,
            is_read=True
        )
        Message.objects.create(
            chat=chat,
            sender=self.passenger,
            content=PASSENGER_MESSAGE,
            is_read=False
        )
        self.chat = chat

    def test_user_has_chat_access(self):
        """Prueba que verifica quién tiene acceso al chat"""
        self.assertTrue(user_has_chat_access(self.driver, self.chat))
        self.assertTrue(user_has_chat_access(self.passenger, self.chat))
        self.assertFalse(user_has_chat_access(self.other_user, self.chat))

    def test_get_user_chats_for_driver(self):
        """Prueba obtener los chats del conductor"""
        chats = get_user_chats(self.driver)
        
        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0]['ride'], self.ride)
        self.assertEqual(chats[0]['last_message'].content, PASSENGER_MESSAGE)

    def test_get_user_chats_for_passenger(self):
        """Prueba obtener los chats del pasajero"""
        chats = get_user_chats(self.passenger)
        
        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0]['ride'], self.ride)
        self.assertEqual(chats[0]['last_message'].content, PASSENGER_MESSAGE)

    def test_get_user_chats_for_user_without_chats(self):
        """Prueba obtener los chats de un usuario sin chats"""
        chats = get_user_chats(self.other_user)
        self.assertEqual(len(chats), 0)