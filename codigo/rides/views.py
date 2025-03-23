from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Ride
from .forms import RideForm, RideSearchForm
from accounts.public import update_last_activity, get_user_profile
from .constants import (
    RIDE_LIST_TEMPLATE, RIDE_DETAIL_TEMPLATE, RIDE_FORM_TEMPLATE,
    RIDE_LIST_URL, RIDE_DETAIL_URL,
    FORM_KEY, RIDE_KEY, RIDES_KEY, SEARCH_FORM_KEY,
    RIDE_CREATED_SUCCESS, RIDE_UPDATED_SUCCESS, RIDE_BOOKED_SUCCESS,
    RIDE_FULL_ERROR, RIDE_OWN_ERROR, RIDE_ALREADY_BOOKED_ERROR,
    FORM_ERROR, NO_PERMISSION_ERROR,
    ORIGIN_KEY, DESTINATION_KEY, DATE_KEY,
    IS_DRIVER_KEY, IS_PASSENGER_KEY, AVAILABLE_SEATS_KEY,
    EDIT_MODE_KEY, PAGE_KEY, RESULTS_PER_PAGE
)

def ride_list(request):
    if request.user.is_authenticated:
        update_last_activity(request.user)
        
    search_form = RideSearchForm(request.GET or None)
    rides = Ride.objects.filter(departure_time__gt=timezone.now())
    
    if search_form.is_valid():
        origin = search_form.cleaned_data.get(ORIGIN_KEY)
        destination = search_form.cleaned_data.get(DESTINATION_KEY)
        date = search_form.cleaned_data.get(DATE_KEY)
        
        if origin:
            rides = rides.filter(origin__icontains=origin)
        if destination:
            rides = rides.filter(destination__icontains=destination)
        if date:
            rides = rides.filter(departure_time__date=date)
    
    paginator = Paginator(rides.order_by('departure_time'), RESULTS_PER_PAGE)
    page_number = request.GET.get(PAGE_KEY)
    page_obj = paginator.get_page(page_number)
    
    return render(request, RIDE_LIST_TEMPLATE, {
        RIDES_KEY: page_obj,
        SEARCH_FORM_KEY: search_form
    })

#TODO Q hace esto?
def search_ride(request):
    if request.user.is_authenticated:
        update_last_activity(request.user)
    
    # Obtener parámetros de búsqueda
    query_origin = request.GET.get(ORIGIN_KEY, '')
    query_destination = request.GET.get(DESTINATION_KEY, '')
    
    rides = Ride.objects.filter(departure_time__gt=timezone.now())
    
    if query_origin:
        rides = rides.filter(origin__icontains=query_origin)
    if query_destination:
        rides = rides.filter(destination__icontains=query_destination)
    
    paginator = Paginator(rides.order_by('departure_time'), RESULTS_PER_PAGE)
    page_number = request.GET.get(PAGE_KEY, 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query_origin': query_origin,
        'query_destination': query_destination
    }
    
    return render(request, 'rides/search_ride.html', context)

@login_required
def ride_detail(request, ride_id):
    update_last_activity(request.user)
    ride = get_object_or_404(Ride, id=ride_id)
    is_driver = request.user == ride.driver
    is_passenger = ride.passengers.filter(id=request.user.id).exists()
    available_seats = ride.total_seats - ride.passengers.count()
    
    return render(request, RIDE_DETAIL_TEMPLATE, {
        RIDE_KEY: ride,
        IS_DRIVER_KEY: is_driver,
        IS_PASSENGER_KEY: is_passenger,
        AVAILABLE_SEATS_KEY: available_seats
    })

@login_required
def book_ride(request, ride_id):
    update_last_activity(request.user)
    ride = get_object_or_404(Ride, id=ride_id)
    
    # Verificar si el usuario ya es pasajero
    if ride.passengers.filter(id=request.user.id).exists():
        messages.warning(request, RIDE_ALREADY_BOOKED_ERROR)
        return redirect(RIDE_DETAIL_URL, ride_id=ride.id)
    
    # Verificar si el usuario es el conductor
    if request.user == ride.driver:
        messages.warning(request, RIDE_OWN_ERROR)
        return redirect(RIDE_DETAIL_URL, ride_id=ride.id)
    
    # Verificar si hay asientos disponibles
    if ride.passengers.count() >= ride.total_seats:
        messages.error(request, RIDE_FULL_ERROR)
        return redirect(RIDE_DETAIL_URL, ride_id=ride.id)
    
    # Añadir al usuario como pasajero
    ride.passengers.add(request.user)
    messages.success(request, RIDE_BOOKED_SUCCESS)
    
    return redirect(RIDE_DETAIL_URL, ride_id=ride.id)

@login_required
def create_ride(request):
    update_last_activity(request.user)
    
    if request.method == 'POST':
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = request.user
            ride.save()
            messages.success(request, RIDE_CREATED_SUCCESS)
            return redirect(RIDE_DETAIL_URL, ride_id=ride.id)
        else:
            messages.error(request, FORM_ERROR)
    else:
        form = RideForm()
    
    return render(request, RIDE_FORM_TEMPLATE, {FORM_KEY: form})

@login_required
def edit_ride(request, ride_id):
    update_last_activity(request.user)
    ride = get_object_or_404(Ride, id=ride_id)
    
    if request.user != ride.driver:
        messages.error(request, NO_PERMISSION_ERROR)
        return redirect(RIDE_DETAIL_URL, ride_id=ride.id)
    
    if request.method == 'POST':
        form = RideForm(request.POST, instance=ride)
        if form.is_valid():
            form.save()
            messages.success(request, RIDE_UPDATED_SUCCESS)
            return redirect(RIDE_DETAIL_URL, ride_id=ride.id)
        else:
            messages.error(request, FORM_ERROR)
    else:
        form = RideForm(instance=ride)
    
    return render(request, RIDE_FORM_TEMPLATE, {
        FORM_KEY: form,
        EDIT_MODE_KEY: True
    })