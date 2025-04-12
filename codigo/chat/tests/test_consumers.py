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
    async def test_chat_consumer_connection(self):
        """Prueba la conexión del consumidor de chat"""
        driver = await self.create_user(DRIVER_USERNAME, DRIVER_PASSWORD)
        passenger = await self.create_user(PASSENGER_USERNAME, PASSENGER_PASSWORD)
        ride = await self.create_ride(driver, passenger)
        
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            WS_CHAT_PATH.format(ride.id)
        )
        communicator.scope["user"] = driver
        communicator.scope["url_route"] = {"kwargs": {"ride_id": str(ride.id)}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        await communicator.disconnect()
    
    async def test_chat_consumer_receive_message(self):
        """Prueba el envío y recepción de mensajes en el consumidor"""
        driver = await self.create_user(DRIVER_USERNAME, DRIVER_PASSWORD)
        passenger = await self.create_user(PASSENGER_USERNAME, PASSENGER_PASSWORD)
        ride = await self.create_ride(driver, passenger)
        
        driver_comm = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            WS_CHAT_PATH.format(ride.id)
        )
        driver_comm.scope["user"] = driver
        driver_comm.scope["url_route"] = {"kwargs": {"ride_id": str(ride.id)}}
        
        passenger_comm = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            WS_CHAT_PATH.format(ride.id)
        )
        passenger_comm.scope["user"] = passenger
        passenger_comm.scope["url_route"] = {"kwargs": {"ride_id": str(ride.id)}}
        
        await driver_comm.connect()
        await passenger_comm.connect()
        
        await driver_comm.send_json_to({
            'message': DRIVER_MESSAGE
        })
        
        response = await passenger_comm.receive_json_from()
        self.assertEqual(response['content'], DRIVER_MESSAGE)
        self.assertEqual(response['sender'], DRIVER_USERNAME)
        
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