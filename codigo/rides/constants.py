"""
Constantes utilizadas en la aplicación de viajes (rides).
"""

# URLs
RIDE_LIST_URL = 'rides:ride_list'
RIDE_DETAIL_URL = 'rides:ride_detail'
BOOK_RIDE_URL = 'rides:book_ride'
CREATE_RIDE_URL = 'rides:create_ride'
EDIT_RIDE_URL = 'rides:edit_ride'
SEARCH_RIDE_URL = 'rides:search_ride'

# Templates
RIDE_LIST_TEMPLATE = 'rides/ride_list.html'
RIDE_DETAIL_TEMPLATE = 'rides/ride_detail.html'
RIDE_FORM_TEMPLATE = 'rides/ride_form.html'

# Keys de formularios y contexto
FORM_KEY = 'form'
RIDE_KEY = 'ride'
RIDES_KEY = 'rides'
SEARCH_FORM_KEY = 'search_form'
ORIGIN_KEY = 'origin'
DESTINATION_KEY = 'destination'
DATE_KEY = 'date'
PASSENGERS_KEY = 'passengers'
DRIVER_KEY = 'driver'
TOTAL_SEATS_KEY = 'total_seats'
PRICE_KEY = 'price'
IS_DRIVER_KEY = 'is_driver'
IS_PASSENGER_KEY = 'is_passenger'
AVAILABLE_SEATS_KEY = 'available_seats'
EDIT_MODE_KEY = 'edit_mode'
PAGE_KEY = 'page'

# Mensajes
RIDE_CREATED_SUCCESS = '¡Viaje creado con éxito!'
RIDE_UPDATED_SUCCESS = '¡Viaje actualizado con éxito!'
RIDE_BOOKED_SUCCESS = '¡Has reservado el viaje con éxito!'
RIDE_FULL_ERROR = 'Lo sentimos, este viaje ya está completo.'
RIDE_OWN_ERROR = 'No puedes reservar un viaje que tú mismo has creado.'
RIDE_ALREADY_BOOKED_ERROR = 'Ya has reservado este viaje anteriormente.'
FORM_ERROR = 'Por favor, corrige los errores en el formulario.'
NO_PERMISSION_ERROR = 'No tienes permiso para editar este viaje.'

# Parámetros y valores
RESULTS_PER_PAGE = 10