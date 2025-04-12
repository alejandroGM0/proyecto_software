# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from decimal import Decimal
from datetime import timedelta

DRIVER_USERNAME = 'conductor'
DRIVER_EMAIL = 'conductor@example.com'
DRIVER_PASSWORD = 'contraseña123'

PASSENGER_USERNAME = 'pasajero'
PASSENGER_EMAIL = 'pasajero@example.com'
PASSENGER_PASSWORD = 'contraseña123'

OTHER_USERNAME = 'otro'
OTHER_EMAIL = 'otro@example.com'
OTHER_PASSWORD = 'contraseña123'

RIDE_ORIGIN = 'Madrid'
RIDE_DESTINATION = 'Barcelona'
RIDE_TOTAL_SEATS = 3
RIDE_PRICE = Decimal('25.50')
RIDE_DAYS_IN_FUTURE = 2

DRIVER_MESSAGE = 'Hola, soy el conductor'
PASSENGER_MESSAGE = 'Hola, soy el pasajero'

URL_RIDE_CHAT = 'chat:ride_chat'
URL_GET_MESSAGES = 'chat:get_messages'

TEMPLATE_CHAT = 'chat/chat.html'

CONTEXT_CHATS_DATA = 'chats_data'
CONTEXT_SELECTED_RIDE = 'selected_ride'

WS_CHAT_PATH = "/ws/chat/{0}/"
