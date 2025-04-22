# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
Constantes para las pruebas del dashboard.
"""
from django.utils import timezone
from datetime import timedelta

# Usuarios
ADMIN_USERNAME = 'admin_test'
ADMIN_EMAIL = 'admin@test.com'
ADMIN_PASSWORD = 'admin12345'

REGULAR_USERNAME = 'user_test'
REGULAR_EMAIL = 'user@test.com'
REGULAR_PASSWORD = 'user12345'

# Periodos
TEST_PERIOD_TODAY = 'today'
TEST_PERIOD_WEEK = 'week'
TEST_PERIOD_MONTH = 'month'
TEST_PERIOD_YEAR = 'year'
TEST_PERIOD_ALL = 'all'

# URLs y templates
URL_DASHBOARD = 'dashboard:dashboard'
URL_RIDE_MANAGEMENT = 'dashboard:ride_management'
URL_USER_MANAGEMENT = 'dashboard:user_management'
URL_CHAT_MANAGEMENT = 'dashboard:chat_management'
URL_TRIP_STATS = 'dashboard:trip_stats'
URL_MSG_STATS = 'dashboard:msg_stats'  # Corregido
URL_REPORT_STATS = 'dashboard:report_stats'
URL_USER_STATS = 'dashboard:user_stats'


# URLs para APIs
URL_API_TRIPS = 'dashboard:api_trips'
URL_API_MESSAGES = 'dashboard:api_messages'
URL_API_REPORTS = 'dashboard:api_reports'
URL_API_USERS = 'dashboard:api_users'
URL_API_PAYMENTS = 'dashboard:api_payments'
URL_GET_CHAT_MESSAGES = 'dashboard:get_chat_messages'

TEMPLATE_DASHBOARD = 'dashboard/dashboard.html'
TEMPLATE_RIDE_MANAGEMENT = 'dashboard/ride_management.html'
TEMPLATE_USER_MANAGEMENT = 'dashboard/user_management.html'
TEMPLATE_CHAT_MANAGEMENT = 'dashboard/chat_management.html'
TEMPLATE_TRIP_STATS = 'dashboard/trip_stats.html'
TEMPLATE_MSG_STATS = 'dashboard/msg_stats.html'
TEMPLATE_REPORT_STATS = 'dashboard/report_stats.html'
TEMPLATE_USER_STATS = 'dashboard/user_stats.html'
TEMPLATE_REPORT_DETAIL = 'dashboard/report_detail.html'

# Fechas
DAYS_FUTURE = 5
DAYS_PAST = 5

# Datos de prueba
TEST_ORIGIN = 'Madrid'
TEST_DESTINATION = 'Barcelona'
TEST_SEATS = 3
TEST_PRICE = 25.0