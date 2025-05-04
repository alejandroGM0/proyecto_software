# ==========================================
# Autor: David Colás Martín
# ==========================================
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.test import RequestFactory, TestCase
from django.utils import timezone
from reviews import _utils
from reviews.constants import NO_PERMISSION_ERROR, REVIEW_ALREADY_EXISTS_ERROR
from reviews.models import Review
from reviews.tests.test_constants import *
from rides.models import Ride


class ReviewUtilsTests(TestCase):
    """Pruebas para las funciones de utilidad del módulo de valoraciones."""

    def setUp(self):
        """Configura los datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para las funciones de utilidad...")

        self.factory = RequestFactory()

        # Crear usuarios
        self.driver = User.objects.create_user(
            username=DRIVER_USERNAME, email=DRIVER_EMAIL, password=DRIVER_PASSWORD
        )

        self.passenger = User.objects.create_user(
            username=PASSENGER_USERNAME,
            email=PASSENGER_EMAIL,
            password=PASSENGER_PASSWORD,
        )

        self.other_user = User.objects.create_user(
            username=OTHER_USERNAME, email=OTHER_EMAIL, password=OTHER_PASSWORD
        )

        # Crear viajes
        past_date = timezone.now() - timedelta(days=RIDE_DAYS_PAST)
        future_date = timezone.now() + timedelta(days=RIDE_DAYS_FUTURE)

        self.past_ride = Ride.objects.create(
            driver=self.driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=past_date,
            total_seats=RIDE_SEATS,
            price=RIDE_PRICE,
        )
        self.past_ride.passengers.add(self.passenger)

        self.future_ride = Ride.objects.create(
            driver=self.driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=future_date,
            total_seats=RIDE_SEATS,
            price=RIDE_PRICE,
        )
        self.future_ride.passengers.add(self.passenger)

        # Crear valoración
        self.review = Review.objects.create(
            ride=self.past_ride,
            user=self.passenger,
            rating=REVIEW_RATING,
            comment=REVIEW_COMMENT,
        )

        print("Se han creado los datos para las pruebas de utilidades.")

    def test_get_review_or_404(self):
        """Prueba la función get_review_or_404."""
        print("\nProbando get_review_or_404...")

        review = _utils.get_review_or_404(self.review.id)
        self.assertEqual(review, self.review)

        with self.assertRaises(Exception):
            _utils.get_review_or_404(99999)

    def test_get_ride_or_404(self):
        """Prueba la función get_ride_or_404."""
        print("\nProbando get_ride_or_404...")

        ride = _utils.get_ride_or_404(self.past_ride.id)
        self.assertEqual(ride, self.past_ride)

        with self.assertRaises(Exception):
            _utils.get_ride_or_404(99999)

    def test_check_review_permission(self):
        """Prueba la función check_review_permission."""
        print("\nProbando check_review_permission...")

        # Preparar request simulado
        request = self.factory.get("/")
        request.user = self.driver  # El conductor no ha valorado aún

        # Para un viaje finalizado sin valoración previa
        result = _utils.check_review_permission(request, self.past_ride)
        self.assertIsNone(result)  # None indica que tiene permiso

        # Para un viaje futuro
        request.user = self.passenger
        with patch("reviews._utils.messages") as mock_messages:
            with patch("reviews._utils.redirect") as mock_redirect:
                mock_redirect.return_value = "REDIRECT_RESULT"
                result = _utils.check_review_permission(request, self.future_ride)
                self.assertEqual(result, "REDIRECT_RESULT")
                mock_messages.error.assert_called_once()

        # Para un viaje ya valorado por el usuario
        with patch("reviews._utils.messages") as mock_messages:
            with patch("reviews._utils.redirect") as mock_redirect:
                mock_redirect.return_value = "REDIRECT_RESULT"
                result = _utils.check_review_permission(request, self.past_ride)
                self.assertEqual(result, "REDIRECT_RESULT")
                mock_messages.info.assert_called_once_with(
                    request, REVIEW_ALREADY_EXISTS_ERROR
                )

    def test_check_delete_permission(self):
        """Prueba la función check_delete_permission."""
        print("\nProbando check_delete_permission...")

        # Preparar request simulado para el autor
        request = self.factory.get("/")
        request.user = self.passenger

        # El autor puede eliminar
        result = _utils.check_delete_permission(request, self.review)
        self.assertIsNone(result)

        # Otro usuario no puede eliminar
        request.user = self.other_user
        result = _utils.check_delete_permission(request, self.review)
        self.assertIsInstance(result, HttpResponseForbidden)
        self.assertEqual(str(result.content, "utf-8"), NO_PERMISSION_ERROR)

    def test_format_review_for_api(self):
        """Prueba la función format_review_for_api."""
        print("\nProbando format_review_for_api...")

        formatted = _utils.format_review_for_api(self.review)

        self.assertEqual(formatted["id"], self.review.id)
        self.assertEqual(formatted["user"], self.passenger.username)
        self.assertEqual(formatted["ride"]["id"], self.past_ride.id)
        self.assertEqual(formatted["rating"], REVIEW_RATING)
        self.assertEqual(formatted["comment"], REVIEW_COMMENT)

    def test_prepare_contexts(self):
        """Prueba las funciones de preparación de contextos."""
        print("\nProbando funciones de preparación de contextos...")

        # Preparar request simulado
        request = self.factory.get("/")
        request.user = self.passenger

        # prepare_review_form_context
        context = _utils.prepare_review_form_context(request, self.past_ride)
        self.assertIn("form", context)
        self.assertEqual(context["ride"], self.past_ride)

        # prepare_review_list_context
        context = _utils.prepare_review_list_context(request)
        self.assertIn("reviews_given", context)
        self.assertIn("reviews_received", context)

        # prepare_review_detail_context
        context = _utils.prepare_review_detail_context(self.review)
        self.assertEqual(context["review"], self.review)

        # prepare_review_delete_context
        context = _utils.prepare_review_delete_context(self.review)
        self.assertEqual(context["review"], self.review)

    def test_redirect_after_delete(self):
        """Prueba la función redirect_after_delete."""
        print("\nProbando redirect_after_delete...")

        # Con viaje asociado
        with patch("reviews._utils.redirect") as mock_redirect:
            mock_redirect.return_value = "REDIRECT_TO_RIDE"
            result = _utils.redirect_after_delete(self.review)
            self.assertEqual(result, "REDIRECT_TO_RIDE")
            mock_redirect.assert_called_once_with(
                "rides:ride_detail", ride_id=self.past_ride.id
            )

        # Sin viaje asociado
        review_without_ride = Review.objects.create(
            user=self.driver, rating=REVIEW_RATING
        )

        with patch("reviews._utils.redirect") as mock_redirect:
            mock_redirect.return_value = "REDIRECT_TO_LIST"
            result = _utils.redirect_after_delete(review_without_ride)
            self.assertEqual(result, "REDIRECT_TO_LIST")
            mock_redirect.assert_called_once()
