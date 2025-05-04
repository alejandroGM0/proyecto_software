# ==========================================
# Autor: David Colás Martín
# ==========================================
"""
Constantes utilizadas en la aplicación de valoraciones (reviews).
"""

# Namespace de la aplicación
APP_NAMESPACE = "reviews"

# Nombres de URLs
CREATE_REVIEW_NAME = "create"
DELETE_REVIEW_NAME = "delete"
LIST_REVIEWS_NAME = "list"
DETAIL_REVIEW_NAME = "detail"


def get_url_full(name):
    """
    Devuelve el nombre completo de una URL incluyendo el namespace.
    Ejemplo: get_url_full(LIST_REVIEWS_NAME) -> 'reviews:list'
    """
    return f"{APP_NAMESPACE}:{name}"


# Templates
CREATE_REVIEW_TEMPLATE = "create_review.html"
DELETE_REVIEW_TEMPLATE = "delete_review.html"
LIST_REVIEWS_TEMPLATE = "list_review.html"
DETAIL_REVIEW_TEMPLATE = "detail_review.html"

# Claves de contexto
REVIEW_KEY = "review"
REVIEWS_GIVEN_KEY = "reviews_given"
REVIEWS_RECEIVED_KEY = "reviews_received"
RIDE_KEY = "ride"
FORM_KEY = "form"

# Valores para rating
MIN_RATING = 1
MAX_RATING = 5
DEFAULT_RATING = 3

# ID params
RIDE_ID_PARAM = "ride_id"
REVIEW_ID_PARAM = "review_id"

# Mensajes
REVIEW_CREATED_SUCCESS = "Tu valoración ha sido registrada correctamente."
REVIEW_DELETED_SUCCESS = "La valoración ha sido eliminada correctamente."
REVIEW_ALREADY_EXISTS_ERROR = "Ya has valorado este viaje anteriormente."
RIDE_NOT_FINISHED_ERROR = "Solo puedes valorar viajes que ya hayan ocurrido."
NO_PERMISSION_ERROR = "No tienes permiso para realizar esta acción."
NO_PARTICIPATION_ERROR = "Solo puedes valorar viajes en los que hayas participado."
