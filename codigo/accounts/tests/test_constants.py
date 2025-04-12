# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
Fichero de constantes compartidas para los tests de la aplicación accounts.
"""

TEST_USERNAME = 'testuser'
TEST_EMAIL = 'test@example.com'
TEST_PASSWORD = 'testpassword123'
INVALID_PASSWORD = 'contraseña_incorrecta'
TEST_BIO = 'Test biography'
TEST_BIO_ES = 'Esta es una biografía de prueba'
TEST_LOCATION = 'Madrid'
TEST_LOCATION_MADRID = 'Madrid'
TEST_LOCATION_BARCELONA = 'Barcelona'
TEST_LOCATION_VALENCIA = 'Valencia'
TEST_PHONE = '123456789'
TEST_NEW_PHONE = '987654321'
TEST_BIRTH_YEAR = 1990
TEST_BIRTH_MONTH = 1
TEST_BIRTH_DAY = 1
NEW_BIO = 'Nueva biografía'

TEST_VEHICLE_MODEL = 'Toyota Corolla'
VEHICLE_MODEL = 'Honda Civic'
TEST_VEHICLE_YEAR = 2018
VEHICLE_YEAR = '2020'
TEST_VEHICLE_COLOR = 'Azul'
VEHICLE_COLOR = 'Blue'

TEST_MUSIC = 'rock'
TEST_MUSIC_ROCK = 'rock'
TEST_MUSIC_POP = 'pop'
TEST_TALK = 'chatty'
TEST_TALK_CHATTY = 'chatty'
TEST_TALK_QUIET = 'quiet'

NEW_USER = 'newuser'
NEW_EMAIL = 'newuser@example.com'
NEW_PASSWORD = 'securepassword123'
EXISTING_USERNAME = 'existinguser'
COMPLEX_PASSWORD = 'complexpassword123'
DIFFERENT_PASSWORD = 'differentpassword'
DIFFERENT_PASSWORD_LONG = 'differentpassword123'
WRONG_PASSWORD = 'wrongpassword'

URL_LOGIN = 'accounts:login'
URL_REGISTER = 'accounts:register'
URL_PROFILE = 'accounts:profile'
URL_PROFILE_VIEW = 'accounts:profile_view'
URL_SETTINGS = 'accounts:settings'
URL_CHANGE_PASSWORD = 'accounts:change_password'

TEMPLATE_LOGIN = 'accounts/login.html'
TEMPLATE_REGISTER = 'accounts/register.html'
TEMPLATE_PROFILE = 'accounts/profile.html'
TEMPLATE_SETTINGS = 'accounts/settings.html'
TEMPLATE_CHANGE_PASSWORD = 'accounts/change_password.html'

FIELD_USERNAME = 'username'
USERNAME_FIELD = 'username'
FIELD_PASSWORD = 'password'
PASSWORD_FIELD = 'password'
FIELD_PASSWORD1 = 'password1'
PASSWORD1_FIELD = 'password1'
FIELD_PASSWORD2 = 'password2'
PASSWORD2_FIELD = 'password2'
FIELD_OLD_PASSWORD = 'old_password'
FIELD_NEW_PASSWORD1 = 'new_password1'
FIELD_NEW_PASSWORD2 = 'new_password2'
FIELD_EMAIL = 'email'
FIELD_LOCATION = 'location'
FIELD_BIO = 'bio'
FIELD_PHONE = 'phone_number'
FIELD_PREF_MUSIC = 'pref_music'
FIELD_PREF_TALK = 'pref_talk'
FIELD_VEHICLE_MODEL = 'vehicle_model'
FIELD_VEHICLE_YEAR = 'vehicle_year'
FIELD_VEHICLE_COLOR = 'vehicle_color'
FIELD_HAS_VEHICLE = 'has_vehicle'
FIELD_PREF_PETS = 'pref_pets'
FIELD_PREF_SMOKING = 'pref_smoking'
FIELD_EMAIL_NOTIFICATIONS = 'email_notifications'
FIELD_SETTINGS_TYPE = 'settings_type'

SETTINGS_TYPE_PROFILE = 'profile'
SETTINGS_TYPE_VEHICLE = 'vehicle'
SETTINGS_TYPE_PREFERENCES = 'preferences'

STATUS_ONLINE = 'En línea recientemente'
STATUS_DAYS = 'Hace 2 días'
STATUS_WEEKS = 'Hace 1 semanas'
DAYS_OFFLINE = 2
WEEKS_OFFLINE = 8

MSG_PROFILE_UPDATED = "actualizada"
MSG_VEHICLE_UPDATED = "vehículo"
MSG_PREFERENCES_UPDATED = "Preferencias de viaje actualizadas correctamente"
ERROR_PASSWORD_MISMATCH = "passwords"
ERROR_USERNAME_TAKEN = "already exists"

CONTEXT_USER_FORM = 'user_form'
CONTEXT_PROFILE_FORM = 'profile_form'
CONTEXT_USER_PROFILE = 'user_profile'
CONTEXT_MESSAGES = 'messages'

LOGIN_URL_PART = 'login'
ON_VALUE = 'on'
PROFILE_STRING_FORMAT = "Perfil de {}"
