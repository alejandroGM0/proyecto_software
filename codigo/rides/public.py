# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
API pública de la aplicación de viajes (rides).
"""
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Avg
from django.shortcuts import get_object_or_404
from .models import Ride
from .constants import (
    RIDE_STATUS_ACTIVE,
    RIDE_STATUS_COMPLETED,
    RIDE_STATUS_CANCELLED
)
from django.db.models import F, ExpressionWrapper, FloatField
from ._utils import (
    get_ride_hourly_data,
    get_ride_daily_data,
    get_ride_monthly_data,
    get_ride_yearly_data,
    get_ride_occupancy_data,
    prepare_ride_stats_result
)

def get_rides_in_period(start_date=None, end_date=None):
    """
    Obtiene los viajes realizados en un periodo específico.
    Si start_date es None, no hay límite inferior de fecha.
    Si end_date es None, no hay límite superior de fecha.
    """
    rides = Ride.objects.all()
    
    if start_date:
        rides = rides.filter(departure_time__date__gte=start_date)
    
    if end_date:
        rides = rides.filter(departure_time__date__lte=end_date)
        
    return rides.order_by('departure_time')

def get_recently_published_rides(limit=5):
    """
    Obtiene los viajes más recientemente publicados basados en su fecha de creación.
    """
    return Ride.objects.all().order_by('-created_at')[:limit]

def get_ride_by_id(ride_id: int) -> Ride:
    """
    Obtiene un viaje por su ID.
    """
    try:
        return Ride.objects.get(id=ride_id)
    except Ride.DoesNotExist:
        return None

def delete_ride(ride_id):
    """
    Elimina un viaje por su ID.
    """
    try:
        ride = get_object_or_404(Ride, id=ride_id)
        ride.delete()
        return True
    except Exception:
        return False

def get_active_rides():
    """
    Obtiene todos los viajes activos (con fecha de salida futura).
    """
    return Ride.objects.filter(departure_time__gt=timezone.now()).order_by('departure_time')

def get_active_rides_today():
    """
    Obtiene el recuento de viajes activos para hoy.
    
    """
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)
    
    return Ride.objects.filter(
        departure_time__gte=timezone.now(),
        departure_time__date__lt=tomorrow
    ).count()

def get_completed_rides():
    """
    Obtiene todos los viajes completados (con fecha de salida pasada).
    """
    return Ride.objects.filter(departure_time__lte=timezone.now()).order_by('-departure_time')

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

def get_seats_available():
    """
    Obtiene el número total de asientos disponibles en viajes activos.
    
    Returns:
        int: Número total de asientos disponibles
    """
    active_rides = Ride.objects.filter(departure_time__gte=timezone.now())
    total_available_seats = 0
    
    for ride in active_rides:
        total_available_seats += ride.seats_available
        
    return total_available_seats

def get_ride_stats_for_dashboard(start_date=None, end_date=None):
    """
    Obtiene estadísticas específicas de viajes para el dashboard.
    Retorna conteos de viajes activos, completados y el precio promedio.
    """
    from datetime import timedelta
    import datetime

    
    all_rides, period_rides, period_rides_by_creation, active_rides, completed_rides = get_basic_ride_data(start_date, end_date)
    
    
    active_count = active_rides.count()
    completed_count = completed_rides.count()
    total_count = period_rides.count()
    avg_price = period_rides.aggregate(Avg('price'))['price__avg'] or 0
    
    
    avg_occupancy = get_ride_occupancy_data(period_rides)
    
    
    top_origins, top_destinations = get_popular_locations(period_rides_by_creation)
    
    
    labels, data_points, period_type = get_temporal_ride_data(period_rides, period_rides_by_creation, start_date, end_date)
    
    
    return prepare_ride_stats_result(
        active_count, completed_count, total_count, avg_price, avg_occupancy,
        top_origins, top_destinations, labels, data_points, period_type
    )

def get_basic_ride_data(start_date, end_date):
    """
    Obtiene los conjuntos de datos básicos de viajes necesarios para las estadísticas.
    """
    import datetime
    
    all_rides = Ride.objects.all()
    now = timezone.now()
    
    
    if isinstance(start_date, datetime.date) and not isinstance(start_date, datetime.datetime):
        start_datetime = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min))
        end_datetime = timezone.make_aware(datetime.datetime.combine(end_date, datetime.time.max))
    else:
        start_datetime = start_date
        end_datetime = end_date
    
    
    if start_datetime and end_datetime:
        
        period_rides_by_creation = Ride.objects.filter(
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        ).order_by('created_at')
        
        
        period_rides = Ride.objects.filter(
            departure_time__gte=start_datetime,
            departure_time__lte=end_datetime
        ).order_by('departure_time')
    else:
        period_rides = all_rides.order_by('departure_time')
        period_rides_by_creation = all_rides
    
    active_rides = all_rides.filter(departure_time__gt=now)
    completed_rides = period_rides.filter(departure_time__lte=now)
    
    return all_rides, period_rides, period_rides_by_creation, active_rides, completed_rides

def get_popular_locations(rides):
    """
    Obtiene los orígenes y destinos más populares de un conjunto de viajes.
    """
    
    top_origins = list(rides.values('origin')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
        .values_list('origin', 'count'))
    
    
    top_destinations = list(rides.values('destination')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
        .values_list('destination', 'count'))
    
    return top_origins, top_destinations

def get_temporal_ride_data(period_rides, period_rides_by_creation, start_date, end_date):
    """
    Obtiene los datos temporales de viajes para el gráfico según el período.
    """
    import datetime
    from datetime import timedelta
    
    labels = []
    data_points = []
    period_type = "daily"
    
    if not start_date or not end_date:
        return ["No hay datos"], [0], period_type
    
    
    if isinstance(start_date, datetime.date) and not isinstance(start_date, datetime.datetime):
        start_datetime = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min))
    else:
        start_datetime = start_date
        
    if isinstance(end_date, datetime.date) and not isinstance(end_date, datetime.datetime):
        end_datetime = timezone.make_aware(datetime.datetime.combine(end_date, datetime.time.max))
    else:
        end_datetime = end_date
    
    
    start_date_only = start_datetime.date() if hasattr(start_datetime, 'date') else start_datetime
    end_date_only = end_datetime.date() if hasattr(end_datetime, 'date') else end_datetime
    now_date = timezone.now().date()
    
    
    is_today = start_date_only == end_date_only == now_date
    
    
    if start_date_only == end_date_only:
        
        labels, data_points = get_ride_hourly_data(
            period_rides_by_creation if is_today else period_rides,
            start_datetime, is_today
        )
        period_type = "hourly"
        
    elif (end_date_only - start_date_only).days < 32:
        
        labels, data_points = get_ride_daily_data(period_rides_by_creation, start_datetime, end_datetime)
        period_type = "daily"
        
    elif (end_date_only - start_date_only).days <= 366:
        
        labels, data_points = get_ride_monthly_data(period_rides_by_creation, start_datetime, end_datetime)
        period_type = "monthly"
        
    else:
        
        labels, data_points = get_ride_yearly_data(period_rides_by_creation, start_datetime, end_datetime)
        period_type = "yearly"
    
    
    if not labels:
        labels = ["No hay datos"]
        data_points = [0]
    
    return labels, data_points, period_type

def get_rides_published_in_period(start_date=None, end_date=None):
    """
    Obtiene el número de viajes publicados en un período específico.
    Se basa en la fecha de creación (created_at) en lugar de la fecha de salida.
    """
    from django.db.models import Count
    
    rides = Ride.objects.all()
    
    if start_date:
        rides = rides.filter(created_at__date__gte=start_date)
    
    if end_date:
        rides = rides.filter(created_at__date__lte=end_date)
    
    return rides.count()

def filter_rides_by_criteria(search='', status='all', origin='', destination='', date_from='', date_to=''):
    """
    Filtra viajes según múltiples criterios para el panel de administración.
    
    """
    from django.db.models import Q
    import datetime
    
    rides = Ride.objects.all().order_by('-departure_time')
    
    if search:
        rides = rides.filter(
            Q(origin__icontains=search) |
            Q(destination__icontains=search) |
            Q(driver__username__icontains=search)
        )
    
    now = timezone.now()
    if status == 'active':
        rides = rides.filter(departure_time__gt=now)
    elif status == 'completed':
        rides = rides.filter(departure_time__lte=now)
    
    if origin:
        rides = rides.filter(origin__icontains=origin)
    
    if destination:
        rides = rides.filter(destination__icontains=destination)
    
    if date_from:
        try:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            rides = rides.filter(departure_time__date__gte=date_from_obj)
        except ValueError:
            pass  
    
    if date_to:
        try:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            rides = rides.filter(departure_time__date__lte=date_to_obj)
        except ValueError:
            pass  
            
    return rides

def get_ride_stats():
    """
    Obtiene estadísticas generales sobre los viajes para el panel de administración.

    """
    from django.db.models import Avg, Count, Sum
    
    now = timezone.now()
    all_rides = Ride.objects.all()
    active_rides = all_rides.filter(departure_time__gt=now)
    completed_rides = all_rides.filter(departure_time__lte=now)
    
    avg_price = all_rides.aggregate(Avg('price'))['price__avg'] or 0
    
    total_passengers = sum(ride.passengers.count() for ride in all_rides)
    
    total_seats = all_rides.aggregate(Sum('total_seats'))['total_seats__sum'] or 0
    occupied_seats = total_passengers
    
    if total_seats > 0:
        occupancy_rate = (occupied_seats / total_seats) * 100
    else:
        occupancy_rate = 0
    
    return {
        'total_rides': all_rides.count(),
        'active_rides': active_rides.count(),
        'completed_rides': completed_rides.count(),
        'avg_price': round(avg_price, 2),
        'total_passengers': total_passengers,
        'occupancy_rate': round(occupancy_rate, 1)
    }