# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
API pública de la aplicación de cuentas (accounts).
"""
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

from .models import UserProfile
from .constants import (
    VEHICLE_INFO_MODEL_KEY, VEHICLE_INFO_YEAR_KEY, VEHICLE_INFO_COLOR_KEY, VEHICLE_INFO_FEATURES_KEY,
    PREFERENCE_MUSIC_KEY, PREFERENCE_TALK_KEY, PREFERENCE_PETS_KEY, PREFERENCE_SMOKING_KEY,
    NOTIFICATION_EMAIL_KEY, NOTIFICATION_MESSAGES_KEY, NOTIFICATION_RIDES_KEY,
    PRIVACY_PROFILE_VISIBLE_KEY, PRIVACY_SHOW_RIDES_HISTORY_KEY,
    INACTIVE_USER_STATUS, LAST_ACTIVE_FIELD
)


def get_user_profile(user):
    """
    Obtiene o crea un perfil de usuario.
    """
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


def get_user_count():
    """
    Obtiene el número total de usuarios en el sistema.
    """
    return User.objects.count()


def get_users_in_period(start_date=None, end_date=None):
    """
    Obtiene los usuarios registrados en un período específico.
    """
    users = User.objects.all()
    
    if start_date:
        users = users.filter(date_joined__date__gte=start_date)
    
    if end_date:
        users = users.filter(date_joined__date__lte=end_date)
        
    return users


def get_active_users(minutes=30):
    """
    Obtiene los usuarios que han estado activos en los últimos minutos especificados.
    """
    threshold_time = timezone.now() - timedelta(minutes=minutes)
    active_profiles = UserProfile.objects.filter(last_active__gte=threshold_time)
    user_ids = active_profiles.values_list('user_id', flat=True)
    
    return User.objects.filter(id__in=user_ids)


def get_recently_registered_users(days=7, limit=5):
    """
    Obtiene los usuarios registrados recientemente.
    """
    recent_date = timezone.now() - timedelta(days=days)
    return User.objects.filter(
        date_joined__gte=recent_date
    ).order_by('-date_joined')[:limit]


def get_user_by_username(username):
    """
    Busca un usuario por su nombre de usuario.
    """
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def get_user_vehicle_info(user):
    """
    Obtiene información del vehículo del usuario.
    """
    profile = get_user_profile(user)

    if not profile.has_vehicle:
        return None

    return {
        VEHICLE_INFO_MODEL_KEY: profile.vehicle_model,
        VEHICLE_INFO_YEAR_KEY: profile.vehicle_year,
        VEHICLE_INFO_COLOR_KEY: profile.vehicle_color,
        VEHICLE_INFO_FEATURES_KEY: profile.vehicle_features
    }


def get_user_preferences(user):
    """
    Obtiene las preferencias de viaje del usuario.
    """
    profile = get_user_profile(user)

    return {
        PREFERENCE_MUSIC_KEY: profile.get_pref_music_display(),
        PREFERENCE_TALK_KEY: profile.get_pref_talk_display(),
        PREFERENCE_PETS_KEY: profile.pref_pets,
        PREFERENCE_SMOKING_KEY: profile.pref_smoking
    }


def get_user_notification_settings(user):
    """
    Obtiene las configuraciones de notificaciones del usuario.
    """
    profile = get_user_profile(user)

    return {
        NOTIFICATION_EMAIL_KEY: profile.email_notifications,
        NOTIFICATION_MESSAGES_KEY: profile.message_notifications,
        NOTIFICATION_RIDES_KEY: profile.ride_notifications
    }


def get_user_privacy_settings(user):
    """
    Obtiene las configuraciones de privacidad del usuario.
    """
    profile = get_user_profile(user)

    return {
        PRIVACY_PROFILE_VISIBLE_KEY: profile.profile_visible,
        PRIVACY_SHOW_RIDES_HISTORY_KEY: profile.show_rides_history
    }


def get_user_age(user):
    """
    Calcula la edad del usuario basada en su fecha de nacimiento.
    """
    profile = get_user_profile(user)

    if not profile.birth_date:
        return None

    today = date.today()
    birth_date = profile.birth_date
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def get_user_activity_status(user):
    """
    Calcula el tiempo desde la última actividad del usuario en minutos.
    """
    profile = get_user_profile(user)

    last_active = profile.last_active
    if not last_active:
        return INACTIVE_USER_STATUS

    now = timezone.now()
    delta = now - last_active

    total_minutes = delta.days * 24 * 60 + delta.seconds // 60

    return total_minutes


def has_vehicle(user):
    """
    Verifica si el usuario tiene un vehículo registrado.
    """
    profile = get_user_profile(user)
    return profile.has_vehicle


def accepts_pets(user):
    """
    Verifica si el usuario acepta mascotas en sus viajes.
    """
    profile = get_user_profile(user)
    return profile.pref_pets


def accepts_smoking(user):
    """
    Verifica si el usuario acepta fumar en sus viajes.
    """
    profile = get_user_profile(user)
    return profile.pref_smoking


def profile_is_visible(user):
    """
    Verifica si el perfil del usuario es visible públicamente.
    """
    profile = get_user_profile(user)
    return profile.profile_visible


def update_last_activity(user):
    """
    Actualiza la marca de tiempo de última actividad del usuario.
    """
    profile = get_user_profile(user)
    profile.last_active = timezone.now()
    profile.save(update_fields=[LAST_ACTIVE_FIELD])


def update_notification_preference(user, notification_type, value):
    """
    Actualiza una preferencia de notificación específica.
    """
    profile = get_user_profile(user)

    if notification_type == NOTIFICATION_EMAIL_KEY:
        profile.email_notifications = value
    elif notification_type == NOTIFICATION_MESSAGES_KEY:
        profile.message_notifications = value
    elif notification_type == NOTIFICATION_RIDES_KEY:
        profile.ride_notifications = value
    else:
        return False

    profile.save(update_fields=[f'{notification_type}_notifications'])
    return True


def delete_user(user_id):
    """
    Elimina un usuario por su ID.
    """
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return True
    except User.DoesNotExist:
        return False
        
        
def filter_users_by_criteria(search='', status='all', from_date='', to_date=''):
    """
    Filtra usuarios según múltiples criterios para el panel de administración.
    """
    from django.db.models import Q
    import datetime
    
    users = User.objects.all().order_by('-date_joined')
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if status == 'active':
        active_threshold = timezone.now() - timedelta(minutes=30)
        user_ids = UserProfile.objects.filter(last_active__gte=active_threshold).values_list('user_id', flat=True)
        users = users.filter(id__in=user_ids)
    elif status == 'inactive':
        active_threshold = timezone.now() - timedelta(minutes=30)
        user_ids = UserProfile.objects.filter(
            Q(last_active__lt=active_threshold) | Q(last_active__isnull=True)
        ).values_list('user_id', flat=True)
        users = users.filter(id__in=user_ids)
    elif status == 'staff':
        users = users.filter(is_staff=True)
    
    if from_date:
        try:
            from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
            users = users.filter(date_joined__date__gte=from_date_obj)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
            users = users.filter(date_joined__date__lte=to_date_obj)
        except ValueError:
            pass
    
    return users