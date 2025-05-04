# ==========================================
# Autor: David Colás Martín
# ==========================================
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ._utils import (check_delete_permission, check_review_permission,
                     get_review_or_404, get_ride_or_404,
                     prepare_review_delete_context,
                     prepare_review_detail_context,
                     prepare_review_form_context, prepare_review_list_context,
                     redirect_after_delete)
from .constants import (CREATE_REVIEW_TEMPLATE, DELETE_REVIEW_TEMPLATE,
                        DETAIL_REVIEW_TEMPLATE, LIST_REVIEWS_TEMPLATE,
                        REVIEW_CREATED_SUCCESS, REVIEW_DELETED_SUCCESS)
from .forms import ReviewForm
from .models import Review
from .public import create_review


@login_required
def create(request, ride_id):
    """
    Vista para crear una nueva reseña para un viaje específico.
    Solo se permite una reseña por usuario y viaje.
    """
    # Obtener el viaje o devolver 404
    ride = get_ride_or_404(ride_id)

    # Verificar permisos para crear la reseña
    check_result = check_review_permission(request, ride)
    if check_result:
        return check_result

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Usar la función create_review de la API pública
            review = create_review(
                user=request.user,
                ride=ride,
                rating=form.cleaned_data["rating"],
                comment=form.cleaned_data["comment"],
            )

            messages.success(request, REVIEW_CREATED_SUCCESS)
            return redirect("rides:ride_detail", ride_id=ride_id)
    else:
        form = ReviewForm()

    context = prepare_review_form_context(request, ride)
    return render(request, CREATE_REVIEW_TEMPLATE, context)


@login_required
def delete(request, review_id):
    """
    Vista para eliminar una reseña.
    Solo el autor de la reseña puede eliminarla.
    """
    review = get_review_or_404(review_id)

    # Verificar permisos para eliminar
    check_result = check_delete_permission(request, review)
    if check_result:
        return check_result

    if request.method == "POST":
        review.delete()
        messages.success(request, REVIEW_DELETED_SUCCESS)
        return redirect_after_delete(review)

    context = prepare_review_delete_context(review)
    return render(request, DELETE_REVIEW_TEMPLATE, context)


@login_required
def list_reviews(request):
    """
    Vista para listar todas las reseñas del usuario actual.
    """
    context = prepare_review_list_context(request)
    return render(request, LIST_REVIEWS_TEMPLATE, context)


@login_required
def detail(request, review_id):
    """
    Vista para ver los detalles de una reseña específica.
    """
    review = get_review_or_404(review_id)

    # Las comprobaciones de permisos se mantienen igual por ahora
    if review.user != request.user and (
        not review.ride
        or (
            review.ride.driver != request.user
            and request.user not in review.ride.passengers.all()
        )
    ):
        from django.http import HttpResponseForbidden

        from .constants import NO_PERMISSION_ERROR

        return HttpResponseForbidden(NO_PERMISSION_ERROR)

    context = prepare_review_detail_context(review)
    return render(request, DETAIL_REVIEW_TEMPLATE, context)
