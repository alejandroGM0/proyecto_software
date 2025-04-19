from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from rides.models import Ride
from reviews.models import Review
from reviews.tests.test_constants import *

class ReviewEndpointSecurityTests(TestCase):
    """
    Pruebas de seguridad para los endpoints del módulo de valoraciones (reviews).
    """
    
    def setUp(self):
        """
        Configura los datos iniciales para las pruebas de seguridad.
        """
        print("\nConfigurando pruebas de seguridad para endpoints de valoraciones...")
        
        self.client = Client()
        
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
        
        # Crear una valoración
        self.review = Review.objects.create(
            ride=self.past_ride,
            user=self.passenger,
            rating=REVIEW_RATING,
            comment=REVIEW_COMMENT
        )
        
        print("Se han creado los datos para las pruebas de seguridad de endpoints.")
    
    def test_unauthorized_access_to_review_list(self):
        """
        Prueba que un usuario no autenticado no puede acceder a la lista de valoraciones.
        """
        print("\nProbando acceso no autorizado a lista de valoraciones...")
        
        # Intentar acceder sin autenticación
        response = self.client.get(reverse(URL_LIST_REVIEWS))
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)
    
    def test_unauthorized_access_to_review_detail(self):
        """
        Prueba que un usuario no autenticado no puede acceder al detalle de una valoración.
        """
        print("\nProbando acceso no autorizado a detalle de valoración...")
        
        # Intentar acceder sin autenticación
        response = self.client.get(reverse(URL_DETAIL_REVIEW, args=[self.review.id]))
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)
    
    def test_unauthorized_access_to_create_review(self):
        """
        Prueba que un usuario no autenticado no puede crear una valoración.
        """
        print("\nProbando acceso no autorizado a creación de valoración...")
        
        # Intentar acceder sin autenticación
        response = self.client.get(reverse(URL_CREATE_REVIEW, args=[self.past_ride.id]))
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)
    
    def test_create_review_for_nonexistent_ride(self):
        """
        Prueba intentar crear una valoración para un viaje que no existe.
        """
        print("\nProbando creación de valoración para viaje inexistente...")
        
        # Login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        # Intentar crear una valoración para un ID de viaje que no existe
        response = self.client.get(reverse(URL_CREATE_REVIEW, args=[9999]))
        
        # Debería dar error 404
        self.assertEqual(response.status_code, 404)
    
    def test_create_review_for_future_ride(self):
        """
        Prueba que no se puede valorar un viaje que aún no ha ocurrido.
        """
        print("\nProbando creación de valoración para viaje futuro...")
        
        # Login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        # Intentar crear una valoración para un viaje futuro
        response = self.client.get(reverse(URL_CREATE_REVIEW, args=[self.future_ride.id]))
        
        # Debería redirigir con un mensaje de error
        self.assertEqual(response.status_code, 302)
        
        # Verificar que no se creó la valoración
        self.assertFalse(Review.objects.filter(ride=self.future_ride, user=self.passenger).exists())
    
    def test_create_review_by_uninvolved_user(self):
        """
        Prueba que un usuario que no participó en el viaje no puede valorarlo.
        """
        print("\nProbando creación de valoración por usuario no implicado...")
        
        # Login como usuario no relacionado con el viaje
        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)
        
        # Intentar crear una valoración
        response = self.client.get(reverse(URL_CREATE_REVIEW, args=[self.past_ride.id]))
        
        # Debería redirigir con un mensaje de error
        self.assertEqual(response.status_code, 302)
        
        # Verificar que no se creó la valoración
        self.assertFalse(Review.objects.filter(ride=self.past_ride, user=self.other_user).exists())
    
    def test_delete_review_by_unauthorized_user(self):
        """
        Prueba que solo el autor puede eliminar su propia valoración.
        """
        print("\nProbando eliminación de valoración por usuario no autorizado...")
        
        # Login como otro usuario
        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)
        
        # Intentar eliminar la valoración
        response = self.client.post(reverse(URL_DELETE_REVIEW, args=[self.review.id]))
        
        # Debería dar error de permiso (403 o redirección)
        self.assertIn(response.status_code, [403, 302])
        
        # Verificar que la valoración sigue existiendo
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())
    
    def test_create_duplicate_review(self):
        """
        Prueba que un usuario no puede crear múltiples valoraciones para el mismo viaje.
        """
        print("\nProbando creación de valoración duplicada...")
        
        # Login como pasajero que ya ha valorado
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        # Intentar crear otra valoración para el mismo viaje
        form_data = {
            'rating': 5,
            'comment': 'Otro comentario'
        }
        response = self.client.post(reverse(URL_CREATE_REVIEW, args=[self.past_ride.id]), form_data)
        
        # Debería redirigir con un mensaje de error
        self.assertEqual(response.status_code, 302)
        
        # Verificar que no se creó una segunda valoración
        self.assertEqual(Review.objects.filter(ride=self.past_ride, user=self.passenger).count(), 1)
    
    def test_csrf_protection_for_create_review(self):
        """
        Prueba que la creación de valoraciones está protegida contra CSRF.
        """
        print("\nProbando protección CSRF para creación de valoraciones...")
        
        # Login como conductor (que no ha valorado aún)
        self.client.login(username=DRIVER_USERNAME, password=DRIVER_PASSWORD)
        
        # Desactivar verificación CSRF para este cliente
        self.client.handler.enforce_csrf_checks = True
        
        # Intentar crear una valoración sin token CSRF
        form_data = {
            'rating': 5,
            'comment': 'Gran experiencia con el pasajero'
        }
        response = self.client.post(reverse(URL_CREATE_REVIEW, args=[self.past_ride.id]), form_data)
        
        # Debería fallar por falta de token CSRF
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_csrf_protection_for_delete_review(self):
        """
        Prueba que la eliminación de valoraciones está protegida contra CSRF.
        """
        print("\nProbando protección CSRF para eliminación de valoraciones...")
        
        # Login como pasajero (autor de la valoración)
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        # Desactivar verificación CSRF para este cliente
        self.client.handler.enforce_csrf_checks = True
        
        # Intentar eliminar la valoración sin token CSRF
        response = self.client.post(reverse(URL_DELETE_REVIEW, args=[self.review.id]))
        
        # Debería fallar por falta de token CSRF
        self.assertEqual(response.status_code, 403)  # Forbidden