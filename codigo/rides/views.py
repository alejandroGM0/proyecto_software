# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from accounts.public import get_user_profile, update_last_activity
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from payments.public import update_payments_on_booking_cancel

from ._utils import filter_rides_complex, get_ride_context, paginate_rides, process_search_params
from .constants import (AVAILABLE_SEATS_KEY, DATE_KEY, DESTINATION_KEY,
                        EDIT_MODE_KEY, FORM_ERROR, FORM_KEY, IS_DRIVER_KEY,
                        IS_PASSENGER_KEY, NO_PERMISSION_ERROR, ORIGIN_KEY,
                        PAGE_KEY, RESULTS_PER_PAGE, RIDE_ALREADY_BOOKED_ERROR,
                        RIDE_BOOKED_SUCCESS, RIDE_CREATED_SUCCESS,
                        RIDE_DETAIL_TEMPLATE, RIDE_DETAIL_URL,
                        RIDE_FORM_TEMPLATE, RIDE_FULL_ERROR, RIDE_KEY,
                        RIDE_LIST_TEMPLATE, RIDE_LIST_URL, RIDE_OWN_ERROR,
                        RIDE_UPDATED_SUCCESS, RIDES_KEY, SEARCH_FORM_KEY,
                        TIME_FROM_KEY, TIME_TO_KEY, PRICE_MIN_KEY, PRICE_MAX_KEY,
                        ALLOWS_SMOKING_KEY, ALLOWS_PETS_KEY, RIDE_BOOKING_CANCELLED_SUCCESS)
from .forms import RideForm, RideSearchForm
from .models import Ride
from .public import (add_passenger_to_ride, get_active_rides, get_ride_by_id,
                     get_rides_by_origin_destination, user_can_book_ride)


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
    page_obj = paginate_rides(
        rides.order_by("departure_time"), page_number, RESULTS_PER_PAGE
    )

    return render(
        request, RIDE_LIST_TEMPLATE, {RIDES_KEY: page_obj, SEARCH_FORM_KEY: search_form}
    )


def search_ride(request):
    if request.user.is_authenticated:
        update_last_activity(request.user)

    search_form = RideSearchForm(request.GET or None)
    
    search_params = process_search_params(request.GET)
    
    rides = filter_rides_complex(
        origin=search_params['origin'],
        destination=search_params['destination'],
        date=search_params['date'],
        time_from=search_params['time_from'],
        time_to=search_params['time_to'],
        min_price=search_params['min_price'],
        max_price=search_params['max_price'],
        allows_smoking=search_params['allows_smoking'],
        allows_pets=search_params['allows_pets']
    )

    page_number = request.GET.get(PAGE_KEY, 1)
    page_obj = paginate_rides(rides, page_number, 6)

    context = {
        "page_obj": page_obj,
        "query_origin": search_params['origin'],
        "query_destination": search_params['destination'],
        "search_form": search_form,
    }

    return render(request, "rides/search_ride.html", context)


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
        return redirect("rides:ride_detail", ride_id=ride.id)
    #CREATE_PAYMENT DEBERIA DE CAMBIAR
    return redirect("payments:create_payment", ride_id=ride.id)


@login_required
def create_ride(request):
    update_last_activity(request.user)

    if request.method == "POST":
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

    if request.method == "POST":
        form = RideForm(request.POST, instance=ride)
        if form.is_valid():
            form.save()
            messages.success(request, RIDE_UPDATED_SUCCESS)
            return redirect(RIDE_DETAIL_URL, ride_id=ride.id)
        else:
            messages.error(request, FORM_ERROR)
    else:
        form = RideForm(instance=ride)

    return render(request, RIDE_FORM_TEMPLATE, {FORM_KEY: form, EDIT_MODE_KEY: True})


@login_required
def cancel_booking(request, ride_id):
    """Cancela la reserva de un viaje para el usuario actual."""
    update_last_activity(request.user)
    
    ride = get_ride_by_id(ride_id)
    if not ride:
        messages.error(request, "El viaje no existe.")
        return redirect(RIDE_LIST_URL)
    
    if request.user not in ride.passengers.all():
        messages.error(request, "No tienes una reserva en este viaje.")
        return redirect(RIDE_DETAIL_URL, ride_id=ride.id)
    
    ride.passengers.remove(request.user)
    ride.save()
    
    update_payments_on_booking_cancel(request.user, ride)

    
    messages.success(request, RIDE_BOOKING_CANCELLED_SUCCESS)
    return redirect(RIDE_DETAIL_URL, ride_id=ride.id)
