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

PASSENGER1_USERNAME = 'pasajero1'
PASSENGER1_EMAIL = 'pasajero1@example.com'
PASSENGER1_PASSWORD = 'contraseña123'

PASSENGER2_USERNAME = 'pasajero2'
PASSENGER2_EMAIL = 'pasajero2@example.com'
PASSENGER2_PASSWORD = 'contraseña123'

OTHER_USERNAME = 'otro'
OTHER_EMAIL = 'otro@example.com'
OTHER_PASSWORD = 'contraseña123'

ORIGIN_CITY = 'Madrid'
DESTINATION_CITY = 'Barcelona'
SECONDARY_ORIGIN = 'Sevilla'
SECONDARY_DESTINATION = 'Valencia'
TERTIARY_ORIGIN = 'Valencia'
TERTIARY_DESTINATION = 'Bilbao'

DEFAULT_SEATS = 3
SECONDARY_SEATS = 2
THIRD_SEATS = 4
DEFAULT_PRICE = Decimal('25.50')
SECONDARY_PRICE = Decimal('30.00')

FUTURE_DAYS = 2
FURTHER_FUTURE_DAYS = 3
PAST_DAYS = -1

DRIVER_MESSAGE = 'Hola, soy el conductor'
PASSENGER_MESSAGE = 'Hola, soy el pasajero'

URL_RIDE_LIST = 'rides:ride_list'
URL_RIDE_DETAIL = 'rides:ride_detail'
URL_BOOK_RIDE = 'rides:book_ride'
URL_CREATE_RIDE = 'rides:create_ride'
URL_SEARCH_RIDE = 'rides:search_ride'
