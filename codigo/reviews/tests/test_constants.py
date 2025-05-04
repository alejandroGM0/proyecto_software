# ==========================================
# Autor: David Colás Martín
# ==========================================
"""
Constantes para los tests de valoraciones (reviews).
"""
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

# Usuarios
DRIVER_USERNAME = "driver_test"
DRIVER_EMAIL = "driver@example.com"
DRIVER_PASSWORD = "driver_password"

PASSENGER_USERNAME = "passenger_test"
PASSENGER_EMAIL = "passenger@example.com"
PASSENGER_PASSWORD = "passenger_password"

OTHER_USERNAME = "other_test"
OTHER_EMAIL = "other@example.com"
OTHER_PASSWORD = "other_password"

# Viajes
RIDE_ORIGIN = "Madrid"
RIDE_DESTINATION = "Barcelona"
RIDE_PRICE = Decimal("25.50")
RIDE_SEATS = 3
RIDE_DAYS_FUTURE = 2
RIDE_DAYS_PAST = 2

# Valoraciones
REVIEW_RATING = 4
REVIEW_COMMENT = "Una valoración de prueba para un viaje satisfactorio."
UPDATED_COMMENT = "Comentario actualizado para la valoración."

# URLs
URL_CREATE_REVIEW = "reviews:create"
URL_DELETE_REVIEW = "reviews:delete"
URL_LIST_REVIEWS = "reviews:list"
URL_DETAIL_REVIEW = "reviews:detail"

# Templates
TEMPLATE_CREATE_REVIEW = "create_review.html"
TEMPLATE_DELETE_REVIEW = "delete_review.html"
TEMPLATE_LIST_REVIEW = "list_review.html"
TEMPLATE_DETAIL_REVIEW = "detail_review.html"
