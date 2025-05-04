# ==========================================
# Autor: David Colás Martín
# ==========================================
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from reviews.constants import DEFAULT_RATING, MAX_RATING, MIN_RATING
from reviews.models import Review
from reviews.tests.test_constants import *
from rides.models import Ride


class ReviewModelTests(TestCase):
    """Pruebas para el modelo Review."""

    def setUp(self):
        """Configura los datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para el modelo Review...")

        # Crear usuarios
        self.driver = User.objects.create_user(
            username=DRIVER_USERNAME, email=DRIVER_EMAIL, password=DRIVER_PASSWORD
        )

        self.passenger = User.objects.create_user(
            username=PASSENGER_USERNAME,
            email=PASSENGER_EMAIL,
            password=PASSENGER_PASSWORD,
        )

        # Crear viaje pasado (para poder valorar)
        past_date = timezone.now() - timedelta(days=RIDE_DAYS_PAST)
        self.ride = Ride.objects.create(
            driver=self.driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=past_date,
            total_seats=RIDE_SEATS,
            price=RIDE_PRICE,
        )
        self.ride.passengers.add(self.passenger)

        # Crear valoración
        self.review = Review.objects.create(
            ride=self.ride,
            user=self.passenger,
            rating=REVIEW_RATING,
            comment=REVIEW_COMMENT,
        )

        print("Se han creado los datos para las pruebas del modelo Review.")

    def test_review_creation(self):
        """Prueba la creación de una valoración."""
        print("\nProbando la creación de una valoración...")

        self.assertEqual(self.review.ride, self.ride)
        self.assertEqual(self.review.user, self.passenger)
        self.assertEqual(self.review.rating, REVIEW_RATING)
        self.assertEqual(self.review.comment, REVIEW_COMMENT)

    def test_review_str(self):
        """Prueba la representación en string del modelo."""
        print("\nProbando la representación en string del modelo...")

        expected_str = f"Review for {self.ride} by {self.passenger.username} - Rating: {REVIEW_RATING}"
        self.assertEqual(str(self.review), expected_str)

    def test_default_rating(self):
        """Prueba el valor por defecto del rating."""
        print("\nProbando el valor por defecto del rating...")

        review = Review.objects.create(ride=self.ride, user=self.driver)

        self.assertEqual(review.rating, MIN_RATING)  # Por defecto es MIN_RATING (1)

    def test_rating_limits(self):
        """Prueba los límites del rating."""
        print("\nProbando los límites del rating...")

        # Probamos un rating por debajo del mínimo
        with self.assertRaises(Exception):
            Review.objects.create(
                ride=self.ride, user=self.driver, rating=MIN_RATING - 1
            )

        # Probamos un rating por encima del máximo
        with self.assertRaises(Exception):
            Review.objects.create(
                ride=self.ride, user=self.driver, rating=MAX_RATING + 1
            )

        # Probamos valores límite que son válidos
        min_review = Review.objects.create(
            ride=self.ride, user=self.driver, rating=MIN_RATING
        )
        self.assertEqual(min_review.rating, MIN_RATING)

        max_review = Review.objects.create(
            ride=self.ride, user=self.driver, rating=MAX_RATING
        )
        self.assertEqual(max_review.rating, MAX_RATING)

    def test_review_without_ride(self):
        """Prueba crear una valoración sin asociar a un viaje."""
        print("\nProbando crear una valoración sin asociar a un viaje...")

        review = Review.objects.create(
            user=self.driver, rating=REVIEW_RATING, comment=REVIEW_COMMENT
        )

        self.assertIsNone(review.ride)
        self.assertEqual(review.user, self.driver)
        self.assertEqual(review.rating, REVIEW_RATING)
        self.assertEqual(review.comment, REVIEW_COMMENT)

    def test_review_without_comment(self):
        """Prueba crear una valoración sin comentario."""
        print("\nProbando crear una valoración sin comentario...")

        review = Review.objects.create(
            ride=self.ride, user=self.driver, rating=REVIEW_RATING
        )

        self.assertEqual(review.ride, self.ride)
        self.assertEqual(review.user, self.driver)
        self.assertEqual(review.rating, REVIEW_RATING)
        self.assertIsNone(review.comment)
