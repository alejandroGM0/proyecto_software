# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from chat.consumers import ChatConsumer
from chat.models import Message
from rides.models import Ride
from .test_constants import *

import pytest

class ChatConsumerTests(TestCase):
    @database_sync_to_async
    def get_ride_and_chat(self, ride_id):
        from rides.models import Ride
        ride = Ride.objects.get(id=ride_id)
        chat = ride.chat
        return ride, chat

    async def test_chat_consumer_connection(self):
        """Prueba la conexión del consumidor de chat"""
        driver = await self.create_user(DRIVER_USERNAME, DRIVER_PASSWORD)
        passenger = await self.create_user(PASSENGER_USERNAME, PASSENGER_PASSWORD)
        ride = await self.create_ride(driver, passenger)
        ride, chat = await self.get_ride_and_chat(ride.id)
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            WS_CHAT_PATH.format(chat.id)
        )
        communicator.scope["user"] = driver
        communicator.scope["url_route"] = {"kwargs": {"chat_id": str(chat.id)}}
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    @database_sync_to_async
    def ensure_passenger_in_chat(self, ride, passenger):
        chat = ride.chat
        chat.participants.add(passenger)
        chat.save()

    async def test_chat_consumer_receive_message(self):
        """Prueba el envío y recepción de mensajes en el consumidor"""
        driver = await self.create_user(DRIVER_USERNAME, DRIVER_PASSWORD)
        passenger = await self.create_user(PASSENGER_USERNAME, PASSENGER_PASSWORD)
        ride = await self.create_ride(driver, passenger)
        ride, chat = await self.get_ride_and_chat(ride.id)
        driver_comm = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            WS_CHAT_PATH.format(chat.id)
        )
        driver_comm.scope["user"] = driver
        driver_comm.scope["url_route"] = {"kwargs": {"chat_id": str(chat.id)}}
        passenger_comm = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            WS_CHAT_PATH.format(chat.id)
        )
        passenger_comm.scope["user"] = passenger
        passenger_comm.scope["url_route"] = {"kwargs": {"chat_id": str(chat.id)}}
        await self.ensure_passenger_in_chat(ride, passenger)
        await driver_comm.connect()
        await passenger_comm.connect()
        await driver_comm.send_json_to({
            'message': DRIVER_MESSAGE
        })
        response = await passenger_comm.receive_json_from()
        self.assertEqual(response['message']['content'], DRIVER_MESSAGE)
        self.assertEqual(response['message']['sender'], DRIVER_USERNAME)
        await driver_comm.disconnect()
        await passenger_comm.disconnect()

    @database_sync_to_async
    def create_user(self, username, password):
        """Utilidad para crear usuarios de forma asíncrona"""
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password=password
        )

    @database_sync_to_async
    def create_ride(self, driver, passenger):
        """Utilidad para crear viajes de forma asíncrona"""
        future_date = timezone.now() + timedelta(days=RIDE_DAYS_IN_FUTURE)
        ride = Ride.objects.create(
            driver=driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=future_date,
            total_seats=RIDE_TOTAL_SEATS,
            price=RIDE_PRICE
        )
        ride.passengers.add(passenger)
        return ride