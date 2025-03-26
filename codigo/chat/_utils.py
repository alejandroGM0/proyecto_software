"""
Funciones de utilidad interna para la aplicación de chat."""
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message
from rides.models import Ride
from accounts.public import update_last_activity
from .public import user_has_chat_access
from .constants import MESSAGE_TYPE_CHAT

def format_message_for_api(message: Message) -> dict:
    """
    Formatea un mensaje para la API JSON.
    """
    return {
        'id': message.id,
        'content': message.content,
        'sender': message.sender.username,
        'timestamp': message.created_at.strftime('%H:%M'),
        'is_read': message.is_read,
        'date': message.created_at.strftime('%Y-%m-%d')
    }

def get_messages_for_ride(ride: Ride) -> list:
    """
    Obtiene todos los mensajes de un viaje formateados para la API.
    """
    messages = ride.messages.all().order_by('created_at')
    return [format_message_for_api(msg) for msg in messages]

def get_chat_participants(ride: Ride) -> list:
    """
    Obtiene todos los participantes de un chat.
    """
    participants = list(ride.passengers.all())
    participants.append(ride.driver)
    return participants

def can_send_message(ride: Ride) -> bool:
    """
    Verifica si un chat está activo para enviar mensajes.
    """
    return ride.is_active

def can_access_chat(user: User, ride_id: int) -> bool:
    """
    Verifica si un usuario tiene acceso al chat de un viaje por ID.
    """
    try:
        ride = Ride.objects.get(id=ride_id)
        return user_has_chat_access(user, ride)
    except Ride.DoesNotExist:
        return False

def save_chat_message(user: User, ride_id: int, message_content: str) -> Message:
    """
    Guarda un mensaje de chat y actualiza la actividad del usuario.
    """
    ride = Ride.objects.get(id=ride_id)
    message = Message.objects.create(
        ride=ride,
        sender=user,
        content=message_content
    )
    update_last_activity(user)
    return message

def format_message_for_websocket(message: str, sender: User) -> dict:
    """
    Formatea un mensaje para ser enviado por WebSocket.
    """
    return {
        'type': MESSAGE_TYPE_CHAT,
        'message': message,
        'sender': sender.username,
        'timestamp': timezone.now().strftime('%H:%M')
    }