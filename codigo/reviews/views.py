from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Review
from rides.models import Ride
from .forms import ReviewForm

@login_required
def create(request, ride_id):
    """
    Vista para crear una nueva reseña para un viaje específico.
    Solo se permite una reseña por usuario y viaje.
    """
    # Obtener el viaje o devolver 404
    ride = get_object_or_404(Ride, pk=ride_id)
    
    # Verificar que el usuario participó en el viaje (como conductor o pasajero)
    if request.user != ride.driver and request.user not in ride.passengers.all():
        messages.error(request, "Solo puedes valorar viajes en los que hayas participado.")
        return redirect('rides:ride_detail', ride_id=ride_id)
    
    # Verificar si el usuario ya ha dejado una reseña para este viaje
    existing_review = Review.objects.filter(ride=ride, user=request.user).first()
    
    if existing_review:
        messages.info(request, "Ya has valorado este viaje anteriormente.")
        return redirect('rides:ride_detail', ride_id=ride_id)
    
    # Validar que el viaje ya ha ocurrido
    from django.utils import timezone
    if ride.departure_time > timezone.now():
        messages.error(request, "Solo puedes valorar viajes que ya hayan ocurrido.")
        return redirect('rides:ride_detail', ride_id=ride_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ride = ride
            review.save()
            
            messages.success(request, "Tu valoración ha sido registrada correctamente.")
            return redirect('rides:ride_detail', ride_id=ride_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'ride': ride
    }
    
    return render(request, 'create_review.html', context)

@login_required
def delete(request, review_id):
    """
    Vista para eliminar una reseña.
    Solo el autor de la reseña puede eliminarla.
    """
    review = get_object_or_404(Review, pk=review_id)
    
    # Verificar que el usuario es el autor de la reseña
    if review.user != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar esta valoración.")
    
    # Almacenar el ride_id para redireccionar después de eliminar
    ride_id = review.ride.id if review.ride else None
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, "La valoración ha sido eliminada correctamente.")
        
        # Redireccionar a la página de detalles del viaje o a la lista de reseñas
        if ride_id:
            return redirect('rides:ride_detail', ride_id=ride_id)
        else:
            return redirect('reviews:list')  # Asumiendo que añadirás esta URL más tarde
    
    context = {
        'review': review
    }
    
    return render(request, 'delete_review.html', context)

@login_required
def list_reviews(request):
    """
    Vista para listar todas las reseñas del usuario actual.
    """
    # Obtener reseñas hechas por el usuario
    reviews_given = Review.objects.filter(user=request.user).order_by('-created_at')
    
    # Obtener reseñas recibidas (para viajes en los que el usuario fue conductor)
    reviews_received = Review.objects.filter(
        ride__driver=request.user
    ).exclude(user=request.user).order_by('-created_at')
    
    context = {
        'reviews_given': reviews_given,
        'reviews_received': reviews_received
    }
    
    return render(request, 'list_review.html', context)

@login_required
def detail(request, review_id):
    """
    Vista para ver los detalles de una reseña específica.
    """
    review = get_object_or_404(Review, pk=review_id)
    
    # Verificar que el usuario tiene permiso para ver esta reseña
    # (es el autor, el conductor o un pasajero del viaje)
    if (review.user != request.user and 
        (not review.ride or 
         (review.ride.driver != request.user and 
          request.user not in review.ride.passengers.all()))):
        return HttpResponseForbidden("No tienes permiso para ver esta valoración.")
    
    context = {
        'review': review
    }
    
    return render(request, 'detail_review.html', context)
