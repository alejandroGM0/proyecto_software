from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from rides.models import Ride
from reviews.models import Review
from reviews import public
from reviews.tests.test_constants import *

class ReviewPublicAPITests(TestCase):
    """Pruebas para las funciones públicas del módulo de valoraciones."""
    
    def setUp(self):
        """Configura los datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para el API público de valoraciones...")
        
        # Crear usuarios
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
        
        # Crear viajes
        past_date = timezone.now() - timedelta(days=RIDE_DAYS_PAST)
        future_date = timezone.now() + timedelta(days=RIDE_DAYS_FUTURE)
        
        self.past_ride = Ride.objects.create(
            driver=self.driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=past_date,
            total_seats=RIDE_SEATS,
            price=RIDE_PRICE
        )
        self.past_ride.passengers.add(self.passenger)
        
        self.future_ride = Ride.objects.create(
            driver=self.driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=future_date,
            total_seats=RIDE_SEATS,
            price=RIDE_PRICE
        )
        self.future_ride.passengers.add(self.passenger)
        
        # Crear valoraciones
        self.review = Review.objects.create(
            ride=self.past_ride,
            user=self.passenger,
            rating=REVIEW_RATING,
            comment=REVIEW_COMMENT
        )
        
        print("Se han creado los datos para las pruebas del API público.")
    
    def test_get_review_by_id(self):
        """Prueba la función para obtener una valoración por ID."""
        print("\nProbando get_review_by_id...")
        
        review = public.get_review_by_id(self.review.id)
        self.assertEqual(review, self.review)
        
        # Prueba con ID inexistente
        review = public.get_review_by_id(99999)
        self.assertIsNone(review)
    
    def test_get_reviews_by_user(self):
        """Prueba la función para obtener valoraciones de un usuario."""
        print("\nProbando get_reviews_by_user...")
        
        reviews = public.get_reviews_by_user(self.passenger)
        self.assertEqual(reviews.count(), 1)
        self.assertEqual(reviews.first(), self.review)
    
    def test_get_reviews_received_by_user(self):
        """Prueba la función para obtener valoraciones recibidas por un usuario."""
        print("\nProbando get_reviews_received_by_user...")
        
        reviews = public.get_reviews_received_by_user(self.driver)
        self.assertEqual(reviews.count(), 1)
        self.assertEqual(reviews.first(), self.review)
    
    def test_get_reviews_for_ride(self):
        """Prueba la función para obtener valoraciones de un viaje."""
        print("\nProbando get_reviews_for_ride...")
        
        reviews = public.get_reviews_for_ride(self.past_ride)
        self.assertEqual(reviews.count(), 1)
        self.assertEqual(reviews.first(), self.review)
    
    def test_get_user_already_reviewed(self):
        """Prueba la función para verificar si un usuario ya ha valorado un viaje."""
        print("\nProbando get_user_already_reviewed...")
        
        # El pasajero ya ha valorado este viaje
        already_reviewed = public.get_user_already_reviewed(self.passenger, self.past_ride)
        self.assertTrue(already_reviewed)
        
        # El conductor no ha valorado este viaje
        already_reviewed = public.get_user_already_reviewed(self.driver, self.past_ride)
        self.assertFalse(already_reviewed)
    
    def test_get_user_average_rating(self):
        """Prueba la función para calcular la puntuación media de un usuario."""
        print("\nProbando get_user_average_rating...")
        
        # Crear más valoraciones para el conductor
        Review.objects.create(
            ride=self.past_ride,
            user=self.other_user,
            rating=5,
            comment="Excelente conductor"
        )
        
        new_ride = Ride.objects.create(
            driver=self.driver,
            origin="Valencia",
            destination="Madrid",
            departure_time=timezone.now() - timedelta(days=5),
            total_seats=2,
            price=30
        )
        
        Review.objects.create(
            ride=new_ride,
            user=self.passenger,
            rating=3,
            comment="Viaje normal"
        )
        
        # Calcular media: (4 + 5 + 3) / 3 = 4
        avg_rating = public.get_user_average_rating(self.driver)
        self.assertEqual(avg_rating, 4)
    
    def test_get_ride_average_rating(self):
        """Prueba la función para calcular la puntuación media de un viaje."""
        print("\nProbando get_ride_average_rating...")
        
        # Añadir otra valoración al mismo viaje
        Review.objects.create(
            ride=self.past_ride,
            user=self.other_user,
            rating=2,
            comment="No me gustó mucho"
        )
        
        # Calcular media: (4 + 2) / 2 = 3
        avg_rating = public.get_ride_average_rating(self.past_ride)
        self.assertEqual(avg_rating, 3)
    
    def test_user_has_participation(self):
        """Prueba la función para verificar si un usuario participó en un viaje."""
        print("\nProbando user_has_participation...")
        
        # El conductor participó
        has_participation = public.user_has_participation(self.driver, self.past_ride)
        self.assertTrue(has_participation)
        
        # El pasajero participó
        has_participation = public.user_has_participation(self.passenger, self.past_ride)
        self.assertTrue(has_participation)
        
        # Otro usuario no participó
        has_participation = public.user_has_participation(self.other_user, self.past_ride)
        self.assertFalse(has_participation)
    
    def test_ride_has_finished(self):
        """Prueba la función para verificar si un viaje ha finalizado."""
        print("\nProbando ride_has_finished...")
        
        # El viaje pasado ha finalizado
        has_finished = public.ride_has_finished(self.past_ride)
        self.assertTrue(has_finished)
        
        # El viaje futuro no ha finalizado
        has_finished = public.ride_has_finished(self.future_ride)
        self.assertFalse(has_finished)
    
    def test_can_review_ride(self):
        """Prueba la función para verificar si un usuario puede valorar un viaje."""
        print("\nProbando can_review_ride...")
        
        # El conductor puede valorar el viaje pasado (no lo ha valorado aún)
        can_review = public.can_review_ride(self.driver, self.past_ride)
        self.assertTrue(can_review)
        
        # El pasajero no puede valorar de nuevo un viaje ya valorado
        can_review = public.can_review_ride(self.passenger, self.past_ride)
        self.assertFalse(can_review)
        
        # Nadie puede valorar un viaje futuro
        can_review = public.can_review_ride(self.passenger, self.future_ride)
        self.assertFalse(can_review)
        
        # Un usuario que no participó no puede valorar
        can_review = public.can_review_ride(self.other_user, self.past_ride)
        self.assertFalse(can_review)
    
    def test_can_delete_review(self):
        """Prueba la función para verificar si un usuario puede eliminar una valoración."""
        print("\nProbando can_delete_review...")
        
        # El autor puede eliminar su valoración
        can_delete = public.can_delete_review(self.passenger, self.review)
        self.assertTrue(can_delete)
        
        # Otro usuario no puede eliminar la valoración
        can_delete = public.can_delete_review(self.other_user, self.review)
        self.assertFalse(can_delete)
    
    def test_create_review(self):
        """Prueba la función para crear una valoración."""
        print("\nProbando create_review...")
        
        # Verificar que el conductor puede valorar
        can_review = public.can_review_ride(self.driver, self.past_ride)
        self.assertTrue(can_review, "El conductor debería poder valorar el viaje")
        
        # El conductor crea una valoración válida
        review = public.create_review(
            user=self.driver,
            ride=self.past_ride,
            rating=5,
            comment="Gran experiencia"
        )
        
        self.assertIsNotNone(review, "La valoración no debería ser None")
        if review:  # Verificamos solo si review no es None
            self.assertEqual(review.user, self.driver)
            self.assertEqual(review.ride, self.past_ride)
            self.assertEqual(review.rating, 5)
            self.assertEqual(review.comment, "Gran experiencia")
        
        # El pasajero intenta crear una valoración duplicada
        review = public.create_review(
            user=self.passenger,
            ride=self.past_ride,
            rating=3,
            comment="Intento duplicado"
        )
        
        self.assertIsNone(review)
        
        # Añadir other_user como pasajero para que pueda valorar el viaje
        self.past_ride.passengers.add(self.other_user)
        
        # Rating fuera de rango se ajusta automáticamente
        review = public.create_review(
            user=self.other_user,
            ride=self.past_ride,
            rating=10,
            comment="Rating muy alto"
        )
        
        self.assertIsNotNone(review, "La valoración con rating ajustado no debería ser None")
        if review:  # Verificamos solo si review no es None
            self.assertEqual(review.rating, 5)  # Se ajusta al máximo
