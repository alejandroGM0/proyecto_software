"""
Funciones de utilidad interna para la aplicación de valoraciones (reviews).
"""
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import Review
from rides.models import Ride
from .forms import ReviewForm
from .constants import (
    CREATE_REVIEW_NAME, DELETE_REVIEW_NAME, LIST_REVIEWS_NAME, DETAIL_REVIEW_NAME,
    REVIEW_KEY, REVIEWS_GIVEN_KEY, REVIEWS_RECEIVED_KEY, RIDE_KEY, FORM_KEY,
    REVIEW_CREATED_SUCCESS, REVIEW_DELETED_SUCCESS, NO_PERMISSION_ERROR,
    NO_PARTICIPATION_ERROR, RIDE_NOT_FINISHED_ERROR, REVIEW_ALREADY_EXISTS_ERROR,
    get_url_full
)
from .public import (
    get_review_by_id, get_reviews_by_user, get_reviews_received_by_user,
    user_has_participation, ride_has_finished, can_review_ride,
    can_delete_review, get_user_already_reviewed
)

def get_review_or_404(review_id):
    """
    Obtiene una valoración o devuelve un 404.
    """
    return get_object_or_404(Review, pk=review_id)

def get_ride_or_404(ride_id):
    """
    Obtiene un viaje o devuelve un 404.
    """
    return get_object_or_404(Ride, pk=ride_id)

def check_review_permission(request, ride):
    """
    Verifica que el usuario tenga permiso para valorar un viaje.
    """
    # Verificar que el usuario participó en el viaje (como conductor o pasajero)
    if not user_has_participation(request.user, ride):
        messages.error(request, NO_PARTICIPATION_ERROR)
        return redirect('rides:ride_detail', ride_id=ride.id)
    
    # Verificar que el viaje ya ha ocurrido
    if not ride_has_finished(ride):
        messages.error(request, RIDE_NOT_FINISHED_ERROR)
        return redirect('rides:ride_detail', ride_id=ride.id)
    
    # Verificar si el usuario ya ha dejado una valoración para este viaje
    if get_user_already_reviewed(request.user, ride):
        messages.info(request, REVIEW_ALREADY_EXISTS_ERROR)
        return redirect('rides:ride_detail', ride_id=ride.id)
    
    return None

def check_delete_permission(request, review):
    """
    Verifica que el usuario tenga permiso para eliminar una valoración.
    """
    if not can_delete_review(request.user, review):
        return HttpResponseForbidden(NO_PERMISSION_ERROR)
    
    return None

def format_review_for_api(review):
    """
    Formatea una valoración para la API JSON.
    """
    return {
        'id': review.id,
        'user': review.user.username,
        'ride': {
            'id': review.ride.id,
            'origin': review.ride.origin,
            'destination': review.ride.destination,
            'driver': review.ride.driver.username,
        } if review.ride else None,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.strftime('%Y-%m-%d %H:%M'),
    }

def prepare_review_form_context(request, ride):
    """
    Prepara el contexto para el formulario de valoración.
    """
    form = ReviewForm(request.POST or None)
    
    return {
        FORM_KEY: form,
        RIDE_KEY: ride
    }

def prepare_review_list_context(request):
    """
    Prepara el contexto para la lista de valoraciones.
    """
    reviews_given = get_reviews_by_user(request.user)
    reviews_received = get_reviews_received_by_user(request.user)
    
    return {
        REVIEWS_GIVEN_KEY: reviews_given,
        REVIEWS_RECEIVED_KEY: reviews_received
    }

def prepare_review_detail_context(review):
    """
    Prepara el contexto para la vista detallada de una valoración.
    """
    return {
        REVIEW_KEY: review
    }

def prepare_review_delete_context(review):
    """
    Prepara el contexto para la confirmación de eliminación de una valoración.
    """
    return {
        REVIEW_KEY: review
    }

def redirect_after_delete(review):
    """
    Redirecciona adecuadamente después de eliminar una valoración.
    """
    # Si el viaje existe, redireccionar a la página de detalles del viaje
    if review.ride:
        return redirect('rides:ride_detail', ride_id=review.ride.id)
    
    # De lo contrario, redireccionar a la lista de valoraciones
    return redirect(get_url_full(LIST_REVIEWS_NAME))
