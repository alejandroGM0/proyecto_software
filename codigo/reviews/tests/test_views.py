from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from rides.models import Ride
from reviews.models import Review
from reviews.constants import REVIEW_CREATED_SUCCESS, REVIEW_DELETED_SUCCESS
from reviews.tests.test_constants import *

class ReviewViewsTests(TestCase):
    """Pruebas para las vistas de valoraciones."""
    
    def setUp(self):
        """Configura los datos iniciales para las pruebas."""
        print("\nConfigurando pruebas para las vistas de valoraciones...")
        
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
        
        print("Se han creado los datos para las pruebas de las vistas.")
        
    def test_create_review_view_get(self):
        """Prueba la carga del formulario para crear una valoración."""
        print("\nProbando la carga del formulario para crear una valoración...")
        
        # Hacer login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        # Probar con otro viaje pasado que aún no ha sido valorado
        new_past_ride = Ride.objects.create(
            driver=self.driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=timezone.now() - timedelta(days=1),
            total_seats=RIDE_SEATS,
            price=RIDE_PRICE
        )
        new_past_ride.passengers.add(self.passenger)
        
        response = self.client.get(reverse(URL_CREATE_REVIEW, args=[new_past_ride.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_CREATE_REVIEW)
        
    def test_create_review_view_post(self):
        """Prueba la creación de una valoración mediante POST."""
        print("\nProbando la creación de una valoración mediante POST...")
        
        # Hacer login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        # Probar con otro viaje pasado que aún no ha sido valorado
        new_past_ride = Ride.objects.create(
            driver=self.driver,
            origin=RIDE_ORIGIN,
            destination=RIDE_DESTINATION,
            departure_time=timezone.now() - timedelta(days=1),
            total_seats=RIDE_SEATS,
            price=RIDE_PRICE
        )
        new_past_ride.passengers.add(self.passenger)
        
        response = self.client.post(reverse(URL_CREATE_REVIEW, args=[new_past_ride.id]), {
            'rating': REVIEW_RATING,
            'comment': REVIEW_COMMENT
        })
        
        # Verificar redirección y mensaje
        self.assertRedirects(response, reverse('rides:ride_detail', args=[new_past_ride.id]))
        
        # Verificar que se creó la valoración
        self.assertTrue(Review.objects.filter(ride=new_past_ride, user=self.passenger).exists())
    
    def test_create_review_future_ride(self):
        """Prueba intentar crear una valoración para un viaje futuro."""
        print("\nProbando intentar crear una valoración para un viaje futuro...")
        
        # Hacer login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        response = self.client.post(reverse(URL_CREATE_REVIEW, args=[self.future_ride.id]), {
            'rating': REVIEW_RATING,
            'comment': REVIEW_COMMENT
        })
        
        # Debería redirigir con un mensaje de error
        self.assertRedirects(response, reverse('rides:ride_detail', args=[self.future_ride.id]))
        
        # Verificar que NO se creó la valoración
        self.assertFalse(Review.objects.filter(ride=self.future_ride, user=self.passenger).exists())
    
    def test_create_review_already_reviewed(self):
        """Prueba intentar crear una valoración para un viaje ya valorado."""
        print("\nProbando intentar crear una valoración para un viaje ya valorado...")
        
        # Hacer login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        response = self.client.post(reverse(URL_CREATE_REVIEW, args=[self.past_ride.id]), {
            'rating': REVIEW_RATING,
            'comment': REVIEW_COMMENT
        })
        
        # Debería redirigir con un mensaje de error
        self.assertRedirects(response, reverse('rides:ride_detail', args=[self.past_ride.id]))
        
        # Verificar que existe solo una valoración
        self.assertEqual(Review.objects.filter(ride=self.past_ride, user=self.passenger).count(), 1)
    
    def test_delete_review_get(self):
        """Prueba la carga del formulario para eliminar una valoración."""
        print("\nProbando la carga del formulario para eliminar una valoración...")
        
        # Hacer login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        response = self.client.get(reverse(URL_DELETE_REVIEW, args=[self.review.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_DELETE_REVIEW)
    
    def test_delete_review_post(self):
        """Prueba la eliminación de una valoración mediante POST."""
        print("\nProbando la eliminación de una valoración mediante POST...")
        
        # Hacer login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        review_id = self.review.id
        ride_id = self.review.ride.id
        
        response = self.client.post(reverse(URL_DELETE_REVIEW, args=[review_id]))
        
        # Verificar redirección y mensaje
        self.assertRedirects(response, reverse('rides:ride_detail', args=[ride_id]))
        
        # Verificar que se eliminó la valoración
        self.assertFalse(Review.objects.filter(id=review_id).exists())
    
    def test_delete_review_unauthorized(self):
        """Prueba intentar eliminar una valoración sin autorización."""
        print("\nProbando intentar eliminar una valoración sin autorización...")
        
        # Hacer login como otro usuario
        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)
        
        response = self.client.post(reverse(URL_DELETE_REVIEW, args=[self.review.id]))
        
        # Debería dar un error de permiso
        self.assertEqual(response.status_code, 403)
        
        # Verificar que la valoración sigue existiendo
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())
    
    def test_list_reviews_view(self):
        """Prueba la vista de lista de valoraciones."""
        print("\nProbando la vista de lista de valoraciones...")
        
        # Hacer login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        response = self.client.get(reverse(URL_LIST_REVIEWS))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_LIST_REVIEW)
        
        # Verificar que las valoraciones están en el contexto
        self.assertIn('reviews_given', response.context)
        self.assertEqual(len(response.context['reviews_given']), 1)
    
    def test_detail_review_view(self):
        """Prueba la vista de detalle de una valoración."""
        print("\nProbando la vista de detalle de una valoración...")
        
        # Hacer login como pasajero
        self.client.login(username=PASSENGER_USERNAME, password=PASSENGER_PASSWORD)
        
        response = self.client.get(reverse(URL_DETAIL_REVIEW, args=[self.review.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TEMPLATE_DETAIL_REVIEW)
        
        # Verificar que la valoración está en el contexto
        self.assertIn('review', response.context)
        self.assertEqual(response.context['review'], self.review)
    
    def test_detail_review_unauthorized(self):
        """Prueba intentar ver detalles de una valoración sin autorización."""
        print("\nProbando intentar ver detalles de una valoración sin autorización...")
        
        # Hacer login como otro usuario
        self.client.login(username=OTHER_USERNAME, password=OTHER_PASSWORD)
        
        response = self.client.get(reverse(URL_DETAIL_REVIEW, args=[self.review.id]))
        
        # Debería dar un error de permiso
        self.assertEqual(response.status_code, 403)
