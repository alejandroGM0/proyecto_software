# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from ._utils import paginate_rides, filter_rides_complex, get_ride_context
from .public import (
    get_ride_by_id, get_active_rides, get_rides_by_origin_destination,
    user_can_book_ride, add_passenger_to_ride
)
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
    
    rides = get_active_rides()
    
    if search_form.is_valid():
        origin = search_form.cleaned_data.get(ORIGIN_KEY)
        destination = search_form.cleaned_data.get(DESTINATION_KEY)
        date = search_form.cleaned_data.get(DATE_KEY)
        
        rides = filter_rides_complex(origin=origin, destination=destination, date=date)
    
    page_number = request.GET.get(PAGE_KEY)
    page_obj = paginate_rides(rides.order_by('departure_time'), page_number, RESULTS_PER_PAGE)
    
    return render(request, RIDE_LIST_TEMPLATE, {
        RIDES_KEY: page_obj,
        SEARCH_FORM_KEY: search_form
    })

def search_ride(request):
    if request.user.is_authenticated:
        update_last_activity(request.user)
    
    query_origin = request.GET.get(ORIGIN_KEY, '')
    query_destination = request.GET.get(DESTINATION_KEY, '')
    
    rides = get_rides_by_origin_destination(query_origin, query_destination)
    
    page_number = request.GET.get(PAGE_KEY, 1)
    page_obj = paginate_rides(rides, page_number, 6)
    
    context = {
        'page_obj': page_obj,
        'query_origin': query_origin,
        'query_destination': query_destination
    }
    
    return render(request, 'rides/search_ride.html', context)

@login_required
def ride_detail(request, ride_id):
    update_last_activity(request.user)
    
    ride = get_ride_by_id(ride_id)
    if not ride:
        return redirect(RIDE_LIST_URL)
    
    context = get_ride_context(ride, request.user)
    
    return render(request, RIDE_DETAIL_TEMPLATE, context)

@login_required
def book_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    if not user_can_book_ride(request.user, ride):
        messages.error(request, "No puedes reservar este viaje.")
        return redirect('rides:ride_detail', ride_id=ride.id)
    add_passenger_to_ride(request.user, ride)
    return redirect('payments:create_payment', ride_id=ride.id)

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
    
    ride = get_ride_by_id(ride_id)
    if not ride:
        return redirect(RIDE_LIST_URL)
    
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