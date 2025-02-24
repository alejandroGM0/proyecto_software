from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ride
from .forms import RideForm
from django.db.models import Q
from django.utils import timezone

def ride_list(request):
    query_origin = request.GET.get('origin', '')
    query_destination = request.GET.get('destination', '')
    
    # Siempre filtrar viajes activos en la lista principal
    rides = Ride.objects.filter(departure_time__gt=timezone.now())
    
    if query_origin:
        rides = rides.filter(origin__icontains=query_origin)
    if query_destination:
        rides = rides.filter(destination__icontains=query_destination)
        
    return render(request, 'rides/ride_list.html', {
        'rides': rides,
        'query_origin': query_origin,
        'query_destination': query_destination,
    })

@login_required
def book_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    
    if request.method == 'POST':
        if not ride.is_active:
            messages.error(request, 'Este viaje ya no está disponible')
        elif ride.seats_available > 0:
            if request.user not in ride.passengers.all():
                ride.passengers.add(request.user)
                messages.success(request, '¡Viaje reservado con éxito!')
            else:
                messages.error(request, 'Ya estás registrado en este viaje')
        else:
            messages.error(request, 'No hay asientos disponibles')
            
    return redirect('rides:ride_list')

@login_required
def create_ride(request):
    if request.method == 'POST':
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = request.user
            ride.save()
            messages.success(request, '¡Viaje creado con éxito!')
            return redirect('rides:ride_list')
    else:
        form = RideForm()
    
    return render(request, 'rides/ride_form.html', {'form': form})

def ride_detail(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    return render(request, 'rides/ride_detail.html', {'ride': ride})

@login_required
def my_rides(request):
    rides_as_driver = Ride.objects.filter(driver=request.user)
    rides_as_passenger = request.user.rides_as_passenger.all()
    return render(request, 'rides/my_rides.html', {
        'rides_as_driver': rides_as_driver,
        'rides_as_passenger': rides_as_passenger,
    })

@login_required
def edit_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, driver=request.user)
    
    # Evitar edición de viajes inactivos
    if not ride.is_active:
        messages.error(request, 'No se pueden editar viajes pasados')
        return redirect('my_rides')
    
    if request.method == 'POST':
        form = RideForm(request.POST, instance=ride)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Viaje actualizado con éxito!')
            return redirect('rides:my_rides')
    else:
        form = RideForm(instance=ride)
    
    return render(request, 'rides/ride_form.html', {
        'form': form,
        'edit_mode': True,
        'ride': ride
    })
