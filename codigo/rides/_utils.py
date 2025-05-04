# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
Funciones de utilidad interna para la aplicación de viajes (rides).
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from django.utils import timezone

from .constants import RESULTS_PER_PAGE
from .models import Ride


def format_ride_for_api(ride: Ride) -> dict:
    """
    Formatea un viaje para la API JSON.
    """
    return {
        "id": ride.id,
        "origin": ride.origin,
        "destination": ride.destination,
        "departure_time": ride.departure_time.strftime("%Y-%m-%d %H:%M"),
        "driver": ride.driver.username,
        "total_seats": ride.total_seats,
        "available_seats": ride.seats_available,
        "price": str(ride.price),
        "formatted_price": ride.get_formatted_price(),
        "is_active": ride.is_active,
        "passengers": [p.username for p in ride.passengers.all()],
    }


def paginate_rides(rides, page_number, per_page=RESULTS_PER_PAGE):
    """
    Pagina un conjunto de viajes.
    """
    paginator = Paginator(rides, per_page)
    return paginator.get_page(page_number)


def filter_rides_complex(
    origin=None,
    destination=None,
    date=None,
    min_price=None,
    max_price=None,
    available_seats=None,
    driver=None,
    time_from=None,
    time_to=None,
    allows_smoking=None,
    allows_pets=None
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
        rides = rides.annotate(available=F("total_seats") - Count("passengers")).filter(
            available__gte=available_seats
        )
    if driver:
        rides = rides.filter(driver__username__icontains=driver)
    
    # Nuevos filtros
    if time_from is not None:
        # Filtra viajes por hora de salida mínima (hora del día)
        rides = rides.filter(departure_time__time__gte=time_from)
    if time_to is not None:
        # Filtra viajes por hora de salida máxima (hora del día)
        rides = rides.filter(departure_time__time__lte=time_to)
    if allows_smoking is not None:
        # Filtra viajes donde el conductor permite fumar
        rides = rides.filter(driver__profile__pref_smoking=allows_smoking)
    if allows_pets is not None:
        # Filtra viajes donde el conductor permite mascotas
        rides = rides.filter(driver__profile__pref_pets=allows_pets)

    return rides.order_by("departure_time")


def process_search_params(request_data):
    """
    Procesa los parámetros de búsqueda de viajes y devuelve los valores formateados
    correctamente para ser usados en el filtrado.
    """
    from datetime import datetime
    from rides.constants import (
        ORIGIN_KEY, DESTINATION_KEY, DATE_KEY, 
        TIME_FROM_KEY, TIME_TO_KEY, 
        PRICE_MIN_KEY, PRICE_MAX_KEY,
        ALLOWS_SMOKING_KEY, ALLOWS_PETS_KEY
    )
    
    origin = request_data.get(ORIGIN_KEY, '')
    destination = request_data.get(DESTINATION_KEY, '')
    date = request_data.get(DATE_KEY, None)
    time_from = request_data.get(TIME_FROM_KEY, None)
    time_to = request_data.get(TIME_TO_KEY, None)
    price_min = request_data.get(PRICE_MIN_KEY, None)
    price_max = request_data.get(PRICE_MAX_KEY, None)
    allows_smoking = request_data.get(ALLOWS_SMOKING_KEY, None)
    allows_pets = request_data.get(ALLOWS_PETS_KEY, None)
    
    date_obj = None
    if date and date.strip():
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            date_obj = None
    
    time_from_obj = None
    if time_from and time_from.strip():
        try:
            time_from_obj = datetime.strptime(time_from, '%H:%M').time()
        except ValueError:
            time_from_obj = None
    
    time_to_obj = None
    if time_to and time_to.strip():
        try:
            time_to_obj = datetime.strptime(time_to, '%H:%M').time()
        except ValueError:
            time_to_obj = None
    
    price_min_val = None
    if price_min and price_min.strip():
        try:
            price_min_val = float(price_min)
        except ValueError:
            price_min_val = None
    
    price_max_val = None
    if price_max and price_max.strip():
        try:
            price_max_val = float(price_max)
        except ValueError:
            price_max_val = None
    
    allows_smoking_val = None
    if allows_smoking == 'on':
        allows_smoking_val = True
    
    allows_pets_val = None
    if allows_pets == 'on':
        allows_pets_val = True
    
    return {
        'origin': origin,
        'destination': destination,
        'date': date_obj,
        'time_from': time_from_obj,
        'time_to': time_to_obj,
        'min_price': price_min_val,
        'max_price': price_max_val,
        'allows_smoking': allows_smoking_val,
        'allows_pets': allows_pets_val
    }


def get_ride_context(ride: Ride, user: User = None) -> dict:
    """
    Obtiene el contexto completo para una vista de detalle de viaje.
    """
    from reviews.public import (get_user_already_reviewed,
                                get_user_average_rating)

    context = {
        "ride": ride,
        "is_driver": user == ride.driver if user else False,
        "is_passenger": ride.passengers.filter(id=user.id).exists() if user else False,
        "available_seats": ride.seats_available,
    }

    # Añadir la valoración media del conductor
    driver_rating = get_user_average_rating(ride.driver)
    context["driver_rating"] = driver_rating

    # Comprobar si el usuario ha valorado el viaje
    if user:
        context["user_has_reviewed"] = get_user_already_reviewed(user, ride)
        # Si el usuario ha valorado el viaje, obtener su valoración
        if context["user_has_reviewed"]:
            from reviews.models import Review

            try:
                user_review = Review.objects.get(user=user, ride=ride)
                context["user_review"] = user_review
            except Review.DoesNotExist:
                context["user_review"] = None

    return context


def get_ride_occupancy_data(rides):
    """
    Calcula la ocupación promedio de un conjunto de viajes.
    """
    from django.db.models import ExpressionWrapper, F, FloatField

    occupancy_data = rides.annotate(
        passenger_count=Count("passengers"),
        occupancy_pct=ExpressionWrapper(
            100.0 * F("passenger_count") / F("total_seats"), output_field=FloatField()
        ),
    ).aggregate(avg_occupancy=Avg("occupancy_pct"))

    return round(occupancy_data["avg_occupancy"] or 0, 1)


def get_ride_hourly_data(rides, start_datetime, is_today):
    """
    Obtiene datos de viajes por hora para un día específico.
    """
    import datetime

    labels = []
    data_points = []

    for hour in range(24):
        hour_start = timezone.make_aware(
            datetime.datetime(
                start_datetime.year, start_datetime.month, start_datetime.day, hour, 0
            )
        )
        hour_end = hour_start + timedelta(hours=1)

        if is_today:
            count = rides.filter(
                created_at__gte=hour_start, created_at__lt=hour_end
            ).count()
        else:
            count = rides.filter(
                departure_time__gte=hour_start, departure_time__lt=hour_end
            ).count()

        labels.append(f"{hour:02d}:00")
        data_points.append(count)

    return labels, data_points


def get_ride_daily_data(rides, start_datetime, end_datetime):
    """
    Obtiene datos de viajes por día para un rango de fechas.
    """
    import datetime

    labels = []
    data_points = []

    current_date = start_datetime.date()
    end_date_only = end_datetime.date()

    while current_date <= end_date_only:
        day_start = timezone.make_aware(
            datetime.datetime.combine(current_date, datetime.time.min)
        )
        day_end = day_start + timedelta(days=1)

        count = rides.filter(created_at__gte=day_start, created_at__lt=day_end).count()

        labels.append(current_date.strftime("%d/%m"))
        data_points.append(count)
        current_date += timedelta(days=1)

    return labels, data_points


def get_ride_monthly_data(rides, start_datetime, end_datetime):
    """
    Obtiene datos de viajes por mes para un rango de fechas.
    """
    import datetime

    labels = []
    data_points = []

    current_month = datetime.datetime(start_datetime.year, start_datetime.month, 1)
    end_month = datetime.datetime(end_datetime.year, end_datetime.month, 1)

    all_months = []
    while current_month <= end_month:
        all_months.append(current_month)

        if current_month.month == 12:
            current_month = datetime.datetime(current_month.year + 1, 1, 1)
        else:
            current_month = datetime.datetime(
                current_month.year, current_month.month + 1, 1
            )

    for month_date in all_months:
        month_start = timezone.make_aware(month_date)

        if month_date.month == 12:
            next_month = datetime.datetime(month_date.year + 1, 1, 1)
        else:
            next_month = datetime.datetime(month_date.year, month_date.month + 1, 1)

        month_end = timezone.make_aware(next_month)

        count = rides.filter(
            created_at__gte=month_start, created_at__lt=month_end
        ).count()

        labels.append(month_date.strftime("%b %Y"))
        data_points.append(count)

    return labels, data_points


def get_ride_yearly_data(rides, start_datetime, end_datetime):
    """
    Obtiene datos de viajes por año para un rango de fechas.
    """
    import datetime

    labels = []
    data_points = []

    start_year = start_datetime.year
    end_year = end_datetime.year

    for year in range(start_year, end_year + 1):
        year_start = timezone.make_aware(datetime.datetime(year, 1, 1))
        year_end = timezone.make_aware(datetime.datetime(year + 1, 1, 1))

        count = rides.filter(
            created_at__gte=year_start, created_at__lt=year_end
        ).count()

        labels.append(str(year))
        data_points.append(count)

    return labels, data_points


def prepare_ride_stats_result(
    active_count,
    completed_count,
    total_count,
    avg_price,
    avg_occupancy,
    top_origins,
    top_destinations,
    labels,
    data_points,
    period_type,
):
    """
    Prepara el resultado final para las estadísticas de viajes.
    """
    result = {
        "active_rides": active_count,
        "completed_rides": completed_count,
        "total_rides": total_count,
        "avg_price": round(avg_price, 2),
        "avg_occupancy": avg_occupancy,
        "top_origins": top_origins,
        "top_destinations": top_destinations,
        "labels": labels,
        "datasets": [{"data": data_points}],
        "period": period_type,
    }

    return result
