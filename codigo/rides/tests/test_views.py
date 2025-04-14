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
from unittest import skip
from rides.tests.test_constants import *
from accounts.models import UserProfile


class RideViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username=DRIVER_USERNAME,
            email=DRIVER_EMAIL,
            password=DRIVER_PASSWORD
        )
        UserProfile.objects.create(user=self.user)

        self.passenger = User.objects.create_user(
            username=PASSENGER_USERNAME,
            email=PASSENGER_EMAIL,
            password=PASSENGER_PASSWORD
        )
        UserProfile.objects.create(user=self.passenger)

        self.future_date = timezone.now() + timedelta(days=FUTURE_DAYS)
        self.ride = Ride.objects.create(
            driver=self.user,
            origin=ORIGIN_CITY,
            destination=DESTINATION_CITY,
            departure_time=self.future_date,
            total_seats=DEFAULT_SEATS,
            price=DEFAULT_PRICE
        )

    def test_ride_list_view(self):
        """Prueba que la vista de lista de viajes funciona correctamente"""
        response = self.client.get(reverse(URL_RIDE_LIST))
        self.assertEqual(response.status_code, 200)

        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        response = self.client.get(reverse(URL_RIDE_LIST))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ORIGIN_CITY)
        self.assertContains(response, DESTINATION_CITY)

    def test_ride_detail_view(self):
        """Prueba que la vista de detalle de viaje funciona correctamente"""
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        response = self.client.get(reverse(URL_RIDE_DETAIL, args=[self.ride.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ORIGIN_CITY)
        self.assertContains(response, DESTINATION_CITY)
        self.assertContains(response, DRIVER_USERNAME)

    def test_book_ride_view(self):
        """Prueba que la reserva de viajes funciona correctamente"""
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)

        self.assertEqual(self.ride.passengers.count(), 0)

        response = self.client.post(reverse(URL_BOOK_RIDE, args=[self.ride.id]))

        self.assertEqual(response.status_code, 302)

        self.ride.refresh_from_db()
        self.assertEqual(self.ride.passengers.count(), 1)
        self.assertTrue(self.ride.passengers.filter(username=PASSENGER_USERNAME).exists())

    def test_create_ride_view(self):
        """Prueba que la creación de viajes funciona correctamente"""
        self.client.login(username=DRIVER_USERNAME, password=DRIVER_PASSWORD)

        future_date_str = (timezone.now() + timedelta(days=FURTHER_FUTURE_DAYS)).strftime('%Y-%m-%d %H:%M')
        ride_data = {
            'origin': SECONDARY_ORIGIN,
            'destination': SECONDARY_DESTINATION,
            'departure_time': future_date_str,
            'total_seats': SECONDARY_SEATS,
            'price': str(SECONDARY_PRICE)
        }

        response = self.client.post(reverse(URL_CREATE_RIDE), ride_data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(Ride.objects.filter(origin=SECONDARY_ORIGIN, destination=SECONDARY_DESTINATION).exists())

    def test_search_ride_view(self):
        """Prueba que la búsqueda de viajes funciona correctamente"""
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)

        search_data = {
            'origin': ORIGIN_CITY,
            'destination': DESTINATION_CITY
        }

        response = self.client.get(reverse(URL_SEARCH_RIDE), search_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ORIGIN_CITY)
        self.assertContains(response, DESTINATION_CITY)

        search_data = {
            'origin': TERTIARY_ORIGIN,
            'destination': TERTIARY_DESTINATION
        }

        response = self.client.get(reverse(URL_SEARCH_RIDE), search_data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, ORIGIN_CITY)
        self.assertNotContains(response, DESTINATION_CITY)