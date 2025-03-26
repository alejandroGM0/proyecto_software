"""
Funciones de utilidad interna para la aplicación de viajes (rides).
"""
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, F, Count
from .models import Ride
from .constants import RESULTS_PER_PAGE

def format_ride_for_api(ride: Ride) -> dict:
    """
    Formatea un viaje para la API JSON.
    """
    return {
        'id': ride.id,
        'origin': ride.origin,
        'destination': ride.destination,
        'departure_time': ride.departure_time.strftime('%Y-%m-%d %H:%M'),
        'driver': ride.driver.username,
        'total_seats': ride.total_seats,
        'available_seats': ride.seats_available,
        'price': str(ride.price),
        'formatted_price': ride.get_formatted_price(),
        'is_active': ride.is_active,
        'passengers': [p.username for p in ride.passengers.all()]
    }

def paginate_rides(rides, page_number, per_page=RESULTS_PER_PAGE):
    """
    Pagina un conjunto de viajes.
    """
    paginator = Paginator(rides, per_page)
    return paginator.get_page(page_number)

def filter_rides_complex(
    origin=None, destination=None, 
    date=None, min_price=None, max_price=None, 
    available_seats=None, driver=None
):
    """
    Filtra viajes con criterios complejos.
    """
    rides = Ride.objects.filter(departure_time__gt=timezone.now())
    
    if origin:
        rides = rides.filter(origin__icontains=origin)
    if destination:
        rides = rides.filter(destination__icontains=destination)
    if date:
        rides = rides.filter(departure_time__date=date)
    if min_price is not None:
        rides = rides.filter(price__gte=min_price)
    if max_price is not None:
        rides = rides.filter(price__lte=max_price)
    if available_seats is not None:
        rides = rides.annotate(
            available=F('total_seats') - Count('passengers')
        ).filter(available__gte=available_seats)
    if driver:
        rides = rides.filter(driver__username__icontains=driver)
    
    return rides.order_by('departure_time')

def get_ride_context(ride: Ride, user: User = None) -> dict:
    """
    Obtiene el contexto completo para una vista de detalle de viaje.
    """
    context = {
        'ride': ride,
        'is_driver': user == ride.driver if user else False,
        'is_passenger': ride.passengers.filter(id=user.id).exists() if user else False,
        'available_seats': ride.seats_available,
    }
    
    return context