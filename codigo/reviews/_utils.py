# ==========================================
# Autor: David Colás Martín
# ==========================================
"""
Funciones de utilidad interna para la aplicación de valoraciones (reviews).
"""

from accounts.public import get_user_profile
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rides.models import Ride

from .constants import (CREATE_REVIEW_NAME, DELETE_REVIEW_NAME,
                        DETAIL_REVIEW_NAME, FORM_KEY, LIST_REVIEWS_NAME,
                        NO_PARTICIPATION_ERROR, NO_PERMISSION_ERROR,
                        REVIEW_ALREADY_EXISTS_ERROR, REVIEW_CREATED_SUCCESS,
                        REVIEW_DELETED_SUCCESS, REVIEW_KEY, REVIEWS_GIVEN_KEY,
                        REVIEWS_RECEIVED_KEY, RIDE_KEY,
                        RIDE_NOT_FINISHED_ERROR, get_url_full)
from .forms import ReviewForm
from .models import Review
from .public import (can_delete_review, can_review_ride, get_review_by_id,
                     get_reviews_by_user, get_reviews_received_by_user,
                     get_user_already_reviewed, ride_has_finished,
                     user_has_participation)


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

    if not user_has_participation(request.user, ride):
        messages.error(request, NO_PARTICIPATION_ERROR)
        return redirect("rides:ride_detail", ride_id=ride.id)

    if not ride_has_finished(ride):
        messages.error(request, RIDE_NOT_FINISHED_ERROR)
        return redirect("rides:ride_detail", ride_id=ride.id)

    if get_user_already_reviewed(request.user, ride):
        messages.info(request, REVIEW_ALREADY_EXISTS_ERROR)
        return redirect("rides:ride_detail", ride_id=ride.id)

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
        "id": review.id,
        "user": review.user.username,
        "ride": (
            {
                "id": review.ride.id,
                "origin": review.ride.origin,
                "destination": review.ride.destination,
                "driver": review.ride.driver.username,
            }
            if review.ride
            else None
        ),
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def prepare_review_form_context(request, ride):
    """
    Prepara el contexto para el formulario de valoración.
    """
    form = ReviewForm(request.POST or None)

    return {FORM_KEY: form, RIDE_KEY: ride}


def prepare_review_list_context(request):
    """
    Prepara el contexto para la lista de valoraciones.
    """

    username = request.GET.get("user")
    target_user = None

    if username:
        from django.contrib.auth.models import User

        try:
            target_user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass

    if not target_user:
        target_user = request.user

    viewing_own = target_user == request.user

    target_profile = get_user_profile(target_user)

    profile_is_private = not viewing_own and not target_profile.profile_visible

    reviews_received = get_reviews_received_by_user(target_user)

    reviews_given = []
    if viewing_own or not profile_is_private:
        reviews_given = get_reviews_by_user(target_user)

    return {
        REVIEWS_GIVEN_KEY: reviews_given,
        REVIEWS_RECEIVED_KEY: reviews_received,
        "target_user": target_user,
        "viewing_own": viewing_own,
        "profile_is_private": profile_is_private,
    }


def prepare_review_detail_context(review):
    """
    Prepara el contexto para la vista detallada de una valoración.
    """
    return {REVIEW_KEY: review}


def prepare_review_delete_context(review):
    """
    Prepara el contexto para la confirmación de eliminación de una valoración.
    """
    return {REVIEW_KEY: review}


def redirect_after_delete(review):
    """
    Redirecciona adecuadamente después de eliminar una valoración.
    """

    if review.ride:
        return redirect("rides:ride_detail", ride_id=review.ride.id)

    return redirect(get_url_full(LIST_REVIEWS_NAME))
