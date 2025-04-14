# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
Funciones de utilidad interna para la aplicación de cuentas (accounts).
"""
import time
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
import stripe
from rides.models import Ride
from .models import UserProfile
from .forms import UserProfileForm
from .constants import *
from .public import (
    get_user_profile, get_user_by_username, get_user_vehicle_info,
    get_user_preferences, get_user_notification_settings, get_user_privacy_settings,
    get_user_age, update_last_activity
)

# Configurar la API de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def get_user_and_profile(request, username):
    """
    Obtiene un usuario y su perfil dado un nombre de usuario.
    """
    user = get_user_by_username(username)
    if not user:
        messages.error(request, USER_NOT_FOUND_ERROR)
        return None, None
    
    user_profile = get_user_profile(user)
    
    if request.user == user:
        update_last_activity(user)
        
    return user, user_profile

def get_user_rides_data(user):
    """
    Obtiene todos los datos relacionados con los viajes del usuario.
    """
    active_rides_as_driver = Ride.objects.filter(
        driver=user,
        departure_time__gt=timezone.now()
    ).order_by('departure_time')
    
    expired_rides_as_driver = Ride.objects.filter(
        driver=user,
        departure_time__lte=timezone.now()
    ).order_by('-departure_time')
    
    active_rides_as_passenger = Ride.objects.filter(
        passengers__id=user.id,
        departure_time__gt=timezone.now()
    ).distinct().order_by('departure_time')
    
    expired_rides_as_passenger = Ride.objects.filter(
        passengers__id=user.id,
        departure_time__lte=timezone.now()
    ).distinct().order_by('-departure_time')
    
    rides_as_passenger = Ride.objects.filter(passengers__id=user.id).distinct()
    
    total_rides = (
        active_rides_as_driver.count() +
        expired_rides_as_driver.count() +
        rides_as_passenger.count()
    )
    
    return {
        ACTIVE_RIDES_DRIVER_KEY: active_rides_as_driver,
        EXPIRED_RIDES_DRIVER_KEY: expired_rides_as_driver,
        ACTIVE_RIDES_PASSENGER_KEY: active_rides_as_passenger,
        EXPIRED_RIDES_PASSENGER_KEY: expired_rides_as_passenger,
        RIDES_PASSENGER_KEY: rides_as_passenger,
        TOTAL_RIDES_KEY: total_rides,
    }

def get_user_profile_data(user):
    """
    Obtiene datos adicionales del perfil del usuario.
    """
    return {
        USER_VEHICLE_KEY: get_user_vehicle_info(user),
        USER_PREFERENCES_KEY: get_user_preferences(user),
        USER_AGE_KEY: get_user_age(user),
    }

def update_account_settings(request):
    """
    Actualiza la configuración de la cuenta del usuario.
    """
    username = request.POST.get(USERNAME_FIELD)
    email = request.POST.get(EMAIL_FIELD)
    
    if username and username != request.user.username:
        request.user.username = username
    
    if email:
        request.user.email = email
    
    request.user.save()
    messages.success(request, ACCOUNT_UPDATE_SUCCESS)

def update_profile_settings(request, user_profile):
    """
    Actualiza la configuración del perfil del usuario.
    """
    if PROFILE_IMAGE_FIELD in request.FILES:
        user_profile.profile_image = request.FILES[PROFILE_IMAGE_FIELD]
    
    profile_data = {
        BIO_FIELD: request.POST.get(BIO_FIELD, ''),
        PHONE_NUMBER_FIELD: request.POST.get(PHONE_NUMBER_FIELD, ''),
        LOCATION_FIELD: request.POST.get(LOCATION_FIELD, ''),
        BIRTH_DATE_FIELD: request.POST.get(BIRTH_DATE_FIELD, None),
    }
    
    profile_data = {k: v for k, v in profile_data.items() if v}
    
    for field, value in profile_data.items():
        setattr(user_profile, field, value)
    user_profile.save()
    messages.success(request, PROFILE_UPDATE_SUCCESS)

def update_vehicle_settings(request, user_profile):
    """
    Actualiza la configuración del vehículo del usuario.
    """
    user_profile.has_vehicle = HAS_VEHICLE_FIELD in request.POST
    
    if user_profile.has_vehicle:
        user_profile.vehicle_model = request.POST.get(VEHICLE_MODEL_FIELD, '')
        user_profile.vehicle_year = request.POST.get(VEHICLE_YEAR_FIELD) or None
        user_profile.vehicle_color = request.POST.get(VEHICLE_COLOR_FIELD, '')
        user_profile.vehicle_features = request.POST.get(VEHICLE_FEATURES_FIELD, '')
    
    user_profile.save()
    messages.success(request, VEHICLE_UPDATE_SUCCESS)

def update_preferences_settings(request, user_profile):
    """
    Actualiza las preferencias de viaje del usuario.
    """
    user_profile.pref_music = request.POST.get(PREF_MUSIC_FIELD, user_profile.pref_music)
    user_profile.pref_talk = request.POST.get(PREF_TALK_FIELD, user_profile.pref_talk)
    user_profile.pref_pets = PREF_PETS_FIELD in request.POST
    user_profile.pref_smoking = PREF_SMOKING_FIELD in request.POST
    
    user_profile.save()
    messages.success(request, PREFERENCES_UPDATE_SUCCESS)

def update_notification_settings(request, user_profile):
    """
    Actualiza las configuraciones de notificaciones del usuario.sdas
    """
    user_profile.email_notifications = EMAIL_NOTIFICATIONS_FIELD in request.POST
    user_profile.message_notifications = MESSAGE_NOTIFICATIONS_FIELD in request.POST
    user_profile.ride_notifications = RIDE_NOTIFICATIONS_FIELD in request.POST
    user_profile.save()
    messages.success(request, NOTIFICATIONS_UPDATE_SUCCESS)

def update_privacy_settings(request, user_profile):
    """
    Actualiza las configuraciones de privacidad del usuario.
    """
    user_profile.profile_visible = PROFILE_VISIBLE_FIELD in request.POST
    user_profile.show_rides_history = SHOW_RIDES_HISTORY_FIELD in request.POST
    user_profile.save()
    messages.success(request, PRIVACY_UPDATE_SUCCESS)

def get_settings_context(user, user_profile):
    """
    Prepara el contexto para la plantilla de configuración.
    """
    return {
        USER_PROFILE_KEY: user_profile,
        PROFILE_FORM_KEY: UserProfileForm(instance=user_profile),
        USER_PREFERENCES_KEY: get_user_preferences(user),
        USER_NOTIFICATIONS_KEY: get_user_notification_settings(user),
        USER_PRIVACY_KEY: get_user_privacy_settings(user),
        USER_VEHICLE_KEY: get_user_vehicle_info(user),
    }

def get_profile_fields(user, profile):
    """
    Obtiene una lista de campos del perfil y verifica si tienen valor.
    """
    return [
        bool(getattr(user, 'first_name', None)),
        bool(getattr(user, 'last_name', None)),
        bool(getattr(user, 'email', None)),
        bool(getattr(profile, 'bio', None)),
        bool(getattr(profile, 'phone_number', None)),
        bool(getattr(profile, 'location', None)),
        bool(getattr(profile, 'birth_date', None)),
        bool(getattr(profile, 'profile_image', None)),
    ]

def get_vehicle_fields(profile):
    """
    Obtiene una lista de campos del vehículo y verifica si tienen valor.
    """
    return [
        bool(profile.vehicle_model),
        bool(profile.vehicle_year),
        bool(profile.vehicle_color)
    ]

def create_stripe_customer(user):
    """
    Crea un cliente de Stripe para un usuario.
    
    Args:
        user: Objeto User de Django
    
    Returns:
        str: ID del cliente de Stripe creado, o None si hay error
    """
    try:
        customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}" if (user.first_name and user.last_name) else user.username,
            metadata={
                'user_id': str(user.id),
                'username': user.username
            }
        )
        return customer.id
    except Exception as e:
        print(f"Error al crear cliente de Stripe: {str(e)}")
        return None

def create_stripe_connect_account(user):
    """
    Crea una cuenta de Stripe Connect para un usuario.
    
    Args:
        user: Objeto User de Django
    
    Returns:
        str: ID de la cuenta de Stripe Connect creada, o None si hay error
    """
    try:
        if not user.email or user.email.strip() == '':
            print(f"Error: El usuario {user.username} no tiene un correo electrónico válido")
            return None
    
        try:
            stripe.Account.list(limit=1)
            print(f"Verificación de permisos de Stripe Connect: OK")
        except stripe.error.PermissionError as perm_error:
            print(f"Error de permisos en Stripe Connect: {str(perm_error)}")
            print("La API key no tiene permisos para crear cuentas Connect")
            return None
        except Exception as check_error:
            print(f"Error al verificar permisos de Stripe Connect: {str(check_error)}")
        
        account = stripe.Account.create(
            type="standard",  # Más simple que 'express' y requiere menos configuración
            country="ES",     # España
            email=user.email.strip(),
            business_type="individual",
            metadata={
                'user_id': str(user.id),
                'username': user.username
            }
        )
        
        print(f"Cuenta Stripe Connect creada con éxito: {account.id}")
        return account.id
        
    except stripe.error.InvalidRequestError as e:
        print(f"Error de solicitud inválida al crear cuenta de Stripe Connect: {str(e)}")
        return None
    except stripe.error.AuthenticationError as e:
        print(f"Error de autenticación en Stripe: {str(e)}")
        return None
    except stripe.error.APIConnectionError as e:
        print(f"Error de conexión con la API de Stripe: {str(e)}")
        return None
    except stripe.error.StripeError as e:
        print(f"Error general de Stripe al crear cuenta Connect: {str(e)}")
        return None
    except Exception as e:
        print(f"Error inesperado al crear cuenta de Stripe Connect: {str(e)}")
        return None

def associate_stripe_accounts_to_user(user):
    """
    Crea y asocia cuentas de Stripe a un usuario.
    
    Args:
        user: Objeto User de Django
    
    Returns:
        tuple: (customer_id, account_id) o (None, None) si hay error
    """
    try:
        profile = user.profile
        
        if profile.stripe_customer_id and profile.stripe_account_id:
            return profile.stripe_customer_id, profile.stripe_account_id
        
        if not profile.stripe_customer_id:
            customer_id = create_stripe_customer(user)
            if customer_id:
                profile.stripe_customer_id = customer_id
        
        if not profile.stripe_account_id:
            account_id = create_stripe_connect_account(user)
            if account_id:
                profile.stripe_account_id = account_id
        
        if profile.stripe_customer_id or profile.stripe_account_id:
            profile.save(update_fields=['stripe_customer_id', 'stripe_account_id'])
        
        return profile.stripe_customer_id, profile.stripe_account_id
    except Exception as e:
        print(f"Error al asociar cuentas de Stripe al usuario: {str(e)}")
        return None, None

def create_stripe_onboarding_link(user):
    """
    Crea un enlace de onboarding para que el usuario complete su registro en Stripe Connect.
    
    Args:
        user: Objeto User de Django
    
    Returns:
        str: URL del enlace de onboarding, o None si hay error
    """
    try:
        profile = user.profile
        
        if not profile.stripe_account_id:
            print(f"Error: El usuario {user.username} no tiene una cuenta de Stripe Connect")
            return None
        
        account_link = stripe.AccountLink.create(
            account=profile.stripe_account_id,
            refresh_url=f"https://{settings.ALLOWED_HOSTS[0]}/accounts/settings/",
            return_url=f"https://{settings.ALLOWED_HOSTS[0]}/accounts/settings/",
            type="account_onboarding",
        )
        
        return account_link.url
    except Exception as e:
        print(f"Error al crear enlace de onboarding de Stripe: {str(e)}")
        return None
