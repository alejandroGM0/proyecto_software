# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from rides.models import Ride
from rides.tests.test_constants import *


class RideModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=DRIVER_USERNAME,
            email=DRIVER_EMAIL,
            password=DRIVER_PASSWORD
        )

        self.pasajero1 = User.objects.create_user(
            username=PASSENGER1_USERNAME,
            email=PASSENGER1_EMAIL,
            password=PASSENGER1_PASSWORD
        )

        self.pasajero2 = User.objects.create_user(
            username=PASSENGER2_USERNAME,
            email=PASSENGER2_EMAIL,
            password=PASSENGER2_PASSWORD
        )

        self.future_date = timezone.now() + timedelta(days=FUTURE_DAYS)

        self.ride = Ride.objects.create(
            driver=self.user,
            origin=ORIGIN_CITY,
            destination=DESTINATION_CITY,
            departure_time=self.future_date,
            total_seats=DEFAULT_SEATS,
            price=DEFAULT_PRICE
        )

    def test_ride_creation(self):
        """Verifica que el viaje se crea correctamente"""
        self.assertEqual(self.ride.driver.username, DRIVER_USERNAME)
        self.assertEqual(self.ride.origin, ORIGIN_CITY)
        self.assertEqual(self.ride.destination, DESTINATION_CITY)
        self.assertEqual(self.ride.total_seats, DEFAULT_SEATS)
        self.assertEqual(self.ride.price, DEFAULT_PRICE)

    def test_get_formatted_price(self):
        """Verifica que el precio formateado es correcto"""
        from django.conf import settings
        expected_price = f"{settings.CURRENCY_SYMBOL}{DEFAULT_PRICE}"
        self.assertEqual(self.ride.get_formatted_price(), expected_price)

    def test_seats_available(self):
        """Verifica que los asientos disponibles se calculan correctamente"""
        self.assertEqual(self.ride.seats_available, DEFAULT_SEATS)

        self.ride.passengers.add(self.pasajero1)
        self.assertEqual(self.ride.seats_available, DEFAULT_SEATS - 1)

        self.ride.passengers.add(self.pasajero2)
        self.assertEqual(self.ride.seats_available, DEFAULT_SEATS - 2)

    def test_is_active(self):
        """Verifica que is_active funciona correctamente"""
        self.assertTrue(self.ride.is_active)

        past_date = timezone.now() + timedelta(days=PAST_DAYS)
        past_ride = Ride.objects.create(
            driver=self.user,
            origin=SECONDARY_ORIGIN,
            destination=SECONDARY_DESTINATION,
            departure_time=past_date,
            total_seats=THIRD_SEATS,
            price=SECONDARY_PRICE
        )

        self.assertFalse(past_ride.is_active)

    def test_string_representation(self):
        """Verifica que la representación en string del modelo es correcta"""
        expected_str = f"{ORIGIN_CITY} → {DESTINATION_CITY} | {DRIVER_USERNAME}"
        self.assertEqual(str(self.ride), expected_str)