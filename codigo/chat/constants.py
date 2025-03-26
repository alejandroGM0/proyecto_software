"""
Constantes para la aplicación de chat
"""

# URLs patterns
URL_RIDE_CHAT = 'chat:ride_chat'
URL_GET_MESSAGES = 'chat:get_messages'
URL_MY_CHATS = 'chat:my_chats'
URL_RIDES_LIST = 'rides:ride_list'

# Plantillas
TEMPLATE_CHAT = 'chat/chat.html'
TEMPLATE_MY_CHATS = 'chat/my_chats.html'

# Contexto
CONTEXT_CHATS_DATA = 'chats_data'
CONTEXT_SELECTED_RIDE = 'selected_ride'
CONTEXT_USER = 'user'
CONTEXT_MESSAGES = 'messages'

# WebSockets
WS_CHAT_PATH = "/ws/chat/{0}/"

# Mensajes
MESSAGE_NO_PERMISSION = 'No tienes permiso para acceder a este chat.'
MESSAGE_SENT = 'sent'
MESSAGE_JOIN = 'join'
MESSAGE_LEAVE = 'leave'

# Otras constantes
MAX_MESSAGE_LENGTH = 500
DATETIME_FORMAT = 'j F Y, H:i'

# Mensajes de error
ERROR_PROCESSING_MESSAGE = 'Error procesando el mensaje'

# Formato de grupos de websocket
CHAT_GROUP_FORMAT = 'chat_{0}'

# Tipos de mensajes de websocket
MESSAGE_TYPE_CHAT = 'chat_message'