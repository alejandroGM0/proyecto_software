# Descripción: Constantes utilizadas en la aplicación de cuentas de usuario.
# Tipos de configuraciones
ACCOUNT_SETTINGS = 'account'
PROFILE_SETTINGS = 'profile'
VEHICLE_SETTINGS = 'vehicle'
PREFERENCES_SETTINGS = 'preferences'
NOTIFICATIONS_SETTINGS = 'notifications'
PRIVACY_SETTINGS = 'privacy'

# Campos de formularios
USERNAME_FIELD = 'username'
EMAIL_FIELD = 'email'
BIO_FIELD = 'bio'
PHONE_NUMBER_FIELD = 'phone_number'
LOCATION_FIELD = 'location'
BIRTH_DATE_FIELD = 'birth_date'
PROFILE_IMAGE_FIELD = 'profile_image'
HAS_VEHICLE_FIELD = 'has_vehicle'
VEHICLE_MODEL_FIELD = 'vehicle_model'
VEHICLE_YEAR_FIELD = 'vehicle_year'
VEHICLE_COLOR_FIELD = 'vehicle_color'
VEHICLE_FEATURES_FIELD = 'vehicle_features'
PREF_MUSIC_FIELD = 'pref_music'
PREF_TALK_FIELD = 'pref_talk'
PREF_PETS_FIELD = 'pref_pets'
PREF_SMOKING_FIELD = 'pref_smoking'
EMAIL_NOTIFICATIONS_FIELD = 'email_notifications'
MESSAGE_NOTIFICATIONS_FIELD = 'message_notifications'
RIDE_NOTIFICATIONS_FIELD = 'ride_notifications'
PROFILE_VISIBLE_FIELD = 'profile_visible'
SHOW_RIDES_HISTORY_FIELD = 'show_rides_history'

# Mensajes de éxito
ACCOUNT_UPDATE_SUCCESS = 'Información de cuenta actualizada correctamente.'
PROFILE_UPDATE_SUCCESS = 'Información personal actualizada correctamente.'
VEHICLE_UPDATE_SUCCESS = 'Información del vehículo actualizada correctamente.'
PREFERENCES_UPDATE_SUCCESS = 'Preferencias de viaje actualizadas correctamente.'
NOTIFICATIONS_UPDATE_SUCCESS = 'Preferencias de notificaciones actualizadas.'
PRIVACY_UPDATE_SUCCESS = 'Preferencias de privacidad actualizadas.'
PASSWORD_UPDATE_SUCCESS = 'Tu contraseña ha sido actualizada correctamente.'
REGISTRATION_SUCCESS = 'Registro exitoso!'
LOGOUT_SUCCESS = 'Has cerrado sesión correctamente.'
LOGIN_SUCCESS = 'Bienvenido {}'

# Mensajes de error
USER_NOT_FOUND_ERROR = 'Usuario no encontrado.'
FORM_ERROR = 'Por favor corrige los errores.'

# Rutas de plantillas
LOGIN_TEMPLATE = 'accounts/login.html'
REGISTER_TEMPLATE = 'accounts/register.html'
PROFILE_TEMPLATE = 'accounts/profile.html'
SETTINGS_TEMPLATE = 'accounts/settings.html'
CHANGE_PASSWORD_TEMPLATE = 'accounts/change_password.html'

# URLs
RIDE_LIST_URL = 'rides:ride_list'
PROFILE_VIEW_URL = 'accounts:profile_view'
SETTINGS_URL = 'accounts:settings'

# Claves de contexto
USER_KEY = 'user'
USER_PROFILE_KEY = 'user_profile'
IS_OWN_PROFILE_KEY = 'is_own_profile'
ACTIVE_RIDES_DRIVER_KEY = 'active_rides_as_driver'
EXPIRED_RIDES_DRIVER_KEY = 'expired_rides_as_driver'
ACTIVE_RIDES_PASSENGER_KEY = 'active_rides_as_passenger'
EXPIRED_RIDES_PASSENGER_KEY = 'expired_rides_as_passenger'
RIDES_PASSENGER_KEY = 'rides_as_passenger'
TOTAL_RIDES_KEY = 'total_rides'
USER_VEHICLE_KEY = 'user_vehicle'
USER_PREFERENCES_KEY = 'user_preferences'
USER_AGE_KEY = 'user_age'
PROFILE_COMPLETION_KEY = 'profile_completion'
PROFILE_FORM_KEY = 'profile_form'
USER_FORM_KEY = 'user_form'
USER_NOTIFICATIONS_KEY = 'user_notifications'
USER_PRIVACY_KEY = 'user_privacy'
FORM_KEY = 'form'

# Claves para información de vehículo
VEHICLE_INFO_MODEL_KEY = 'model'
VEHICLE_INFO_YEAR_KEY = 'year'
VEHICLE_INFO_COLOR_KEY = 'color'
VEHICLE_INFO_FEATURES_KEY = 'features'

# Claves para preferencias de usuario
PREFERENCE_MUSIC_KEY = 'music'
PREFERENCE_TALK_KEY = 'talk'
PREFERENCE_PETS_KEY = 'pets'
PREFERENCE_SMOKING_KEY = 'smoking'

# Claves para notificaciones
NOTIFICATION_EMAIL_KEY = 'email'
NOTIFICATION_MESSAGES_KEY = 'messages'
NOTIFICATION_RIDES_KEY = 'rides'

# Claves para privacidad
PRIVACY_PROFILE_VISIBLE_KEY = 'profile_visible'
PRIVACY_SHOW_RIDES_HISTORY_KEY = 'show_rides_history'

# Listas de campos para completitud del perfil
PROFILE_FIELDS = [
    'first_name',
    'last_name',
    'email',
    'bio',
    'phone_number',
    'location',
    'birth_date',
    'profile_image'
]

VEHICLE_FIELDS = [
    'vehicle_model',
    'vehicle_year',
    'vehicle_color'
]

# Estados y otros valores
INACTIVE_USER_STATUS = -1
LAST_ACTIVE_FIELD = 'last_active'
UPDATE_FIELD_PARAMETER = 'update_fields'
