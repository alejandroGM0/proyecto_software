"""
API pública de la aplicación de viajes (rides).
"""
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Ride

def get_ride_by_id(ride_id: int) -> Ride:
    """
    Obtiene un viaje por su ID.
    """
    try:
        return Ride.objects.get(id=ride_id)
    except Ride.DoesNotExist:
        return None

def get_active_rides():
    """
    Obtiene todos los viajes activos (con fecha de salida futura).
    """
    return Ride.objects.filter(departure_time__gt=timezone.now()).order_by('departure_time')

def get_rides_by_origin_destination(origin=None, destination=None):
    """
    Busca viajes activos por origen y/o destino.
    """
    rides = get_active_rides()
    
    if origin:
        rides = rides.filter(origin__icontains=origin)
    if destination:
        rides = rides.filter(destination__icontains=destination)
        
    return rides

def get_driver_rides(user: User):
    """
    Obtiene todos los viajes creados por un usuario como conductor.
    """
    active_rides = Ride.objects.filter(
        driver=user,
        departure_time__gt=timezone.now()
    ).order_by('departure_time')
    
    expired_rides = Ride.objects.filter(
        driver=user,
        departure_time__lte=timezone.now()
    ).order_by('-departure_time')
    
    return {
        'active': active_rides,
        'expired': expired_rides
    }

def get_passenger_rides(user: User):
    """
    Obtiene todos los viajes en los que un usuario participa como pasajero.
    """
    active_rides = Ride.objects.filter(
        passengers__id=user.id,
        departure_time__gt=timezone.now()
    ).distinct().order_by('departure_time')
    
    expired_rides = Ride.objects.filter(
        passengers__id=user.id,
        departure_time__lte=timezone.now()
    ).distinct().order_by('-departure_time')
    
    return {
        'active': active_rides,
        'expired': expired_rides
    }

def user_can_book_ride(user: User, ride: Ride) -> bool:
    """
    Verifica si un usuario puede reservar un viaje.
    """
    if not ride.is_active:
        return False
    
    if ride.seats_available <= 0:
        return False
    
    if user == ride.driver:
        return False
    
    if ride.passengers.filter(id=user.id).exists():
        return False
    
    return True

def add_passenger_to_ride(user: User, ride: Ride) -> bool:
    """
    Añade un pasajero a un viaje.
    """
    if not user_can_book_ride(user, ride):
        return False
    
    ride.passengers.add(user)
    return True