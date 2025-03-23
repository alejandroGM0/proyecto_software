"""
API pública de la aplicación de cuentas (accounts).
"""
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

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

#TODO HAY Q EVITAR DUPLICIDAD ENTRE PUBLIC Y PRIVATE    
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