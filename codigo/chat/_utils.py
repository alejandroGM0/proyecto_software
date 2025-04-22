# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================


"""
Utilidades para la aplicación de chat.
"""
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message, Chat
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

def get_messages_for_chat(chat):
    """
    Obtiene los mensajes de un chat formateados para la API.
    Solo se llama cuando se visualiza un chat específico.
    """
    messages = Message.objects.filter(chat=chat).order_by('created_at')
    messages_data = []
    
    for message in messages:
        
        date_str = message.created_at.strftime('%d/%m/%Y')
        
        time_str = message.created_at.strftime('%H:%M')
        
        messages_data.append({
            'id': message.id,
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': time_str,
            'date': date_str,
            'is_read': message.is_read,
        })
    
    return messages_data

def can_send_message(chat: Chat) -> bool:
    """
    Verifica si un chat está activo para enviar mensajes.
    Para chats de viaje, depende del estado del viaje.
    Para chats directos, siempre es True.
    """
    if hasattr(chat, 'ride'):
        return chat.ride.is_active
    return True

def can_access_chat(user: User, chat_id: int) -> bool:
    """
    Verifica si un usuario tiene acceso a un chat por ID.
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        return user_has_chat_access(user, chat)
    except Chat.DoesNotExist:
        return False

def save_chat_message(user: User, chat_id: int, message_content: str) -> Message:
    """
    Guarda un mensaje en un chat y actualiza la actividad del usuario.
    """
    chat = Chat.objects.get(id=chat_id)
    message = Message.objects.create(
        chat=chat,
        sender=user,
        content=message_content
    )
    update_last_activity(user)
    return message

def get_chat_participants(ride: Ride) -> list:
    """
    Obtiene todos los participantes de un chat.
    """
    participants = list(ride.passengers.all())
    participants.append(ride.driver)
    return participants

def format_message_for_websocket(message: str, sender: User) -> dict:
    """
    Formatea un mensaje para enviar por WebSocket.
    """
    now = timezone.now()
    return {
        'content': message,
        'sender': sender.username,
        'sender_id': sender.id,
        'timestamp': now.strftime('%H:%M'),
        'date': now.strftime('%Y-%m-%d'),
        'is_read': False
    }

def synchronize_chat_participants(ride):
    """
    Función de utilidad para sincronizar participantes del chat con los de un viaje
    """
    if not hasattr(ride, 'chat') or not ride.chat:
        return
        
    
    ride.chat.participants.add(ride.driver)
    
    
    for passenger in ride.passengers.all():
        ride.chat.participants.add(passenger)