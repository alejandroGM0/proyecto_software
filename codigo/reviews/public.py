"""
API pública de la aplicación de valoraciones (reviews).
"""
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg
from django.core.exceptions import ValidationError

from .models import Review
from rides.models import Ride
from .constants import MIN_RATING, MAX_RATING, DEFAULT_RATING

def get_review_by_id(review_id):
    """
    Obtiene una valoración por su ID.
    """
    try:
        return Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return None

def get_reviews_by_user(user):
    """
    Obtiene todas las valoraciones realizadas por un usuario.
    """
    return Review.objects.filter(user=user).order_by('-created_at')

def get_reviews_received_by_user(user):
    """
    Obtiene todas las valoraciones recibidas por un usuario como conductor.
    """
    return Review.objects.filter(
        ride__driver=user
    ).exclude(user=user).order_by('-created_at')

def get_reviews_for_ride(ride):
    """
    Obtiene todas las valoraciones para un viaje específico.
    """
    return Review.objects.filter(ride=ride).order_by('-created_at')

def get_user_already_reviewed(user, ride):
    """
    Verifica si un usuario ya ha valorado un viaje específico.
    """
    return Review.objects.filter(user=user, ride=ride).exists()

def get_user_average_rating(user):
    """
    Calcula la puntuación media recibida por un usuario como conductor.
    """
    average = Review.objects.filter(
        ride__driver=user
    ).exclude(user=user).aggregate(Avg('rating'))['rating__avg']
    
    return average if average is not None else 0

def get_ride_average_rating(ride):
    """
    Calcula la puntuación media de un viaje.
    """
    average = Review.objects.filter(ride=ride).aggregate(Avg('rating'))['rating__avg']
    return average if average is not None else 0

def user_has_participation(user, ride):
    """
    Verifica si un usuario participó en un viaje, ya sea como conductor o pasajero.
    """
    return user == ride.driver or ride.passengers.filter(id=user.id).exists()

def ride_has_finished(ride):
    """
    Verifica si un viaje ya ha finalizado.
    """
    return ride.departure_time < timezone.now()

def can_review_ride(user, ride):
    """
    Verifica si un usuario puede valorar un viaje.
    """
    # Verificar que el viaje ha terminado
    if not ride_has_finished(ride):
        return False
    
    # Verificar que el usuario participó en el viaje
    if not user_has_participation(user, ride):
        return False
    
    # Verificar que no haya valorado el viaje anteriormente
    if get_user_already_reviewed(user, ride):
        return False
    
    return True

def can_delete_review(user, review):
    """
    Verifica si un usuario puede eliminar una valoración.
    """
    # Solo el autor de la valoración puede eliminarla
    return user == review.user

def create_review(user, ride, rating, comment=None):
    """
    Crea una nueva valoración para un viaje.
    """
    if not can_review_ride(user, ride):
        return None
    
    # Validar rating
    rating = max(MIN_RATING, min(MAX_RATING, int(rating)))
    
    try:
        review = Review.objects.create(
            ride=ride,
            user=user,
            rating=rating,
            comment=comment
        )
        return review
    except ValidationError:
        return None
