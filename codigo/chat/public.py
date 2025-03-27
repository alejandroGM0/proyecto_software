"""
API pública de la aplicación de chat.
"""
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from .models import Message, Chat
from rides.models import Ride
from accounts.public import update_last_activity

def user_has_chat_access(user: User, chat: Chat) -> bool:
    """
    Verifica si un usuario tiene acceso a un chat.
    """
    return chat.participants.filter(id=user.id).exists()

def get_user_chats(user: User):
    """
    Obtiene todos los chats en los que participa un usuario.
    Incluye tanto chats de viajes como chats directos.
    """
    # Obtener todos los chats del usuario
    user_chats = Chat.objects.filter(participants=user).distinct()
    
    chats_data = []
    for chat in user_chats:
        last_message = chat.messages.order_by('-created_at').first()
        
        data = {
            'chat': chat,
            'last_message': last_message,
            'is_ride_chat': hasattr(chat, 'ride')
        }
        
        # Si es un chat de viaje, añadimos la información del viaje
        if hasattr(chat, 'ride'):
            data['ride'] = chat.ride
            
        chats_data.append(data)
    
    # Ordenamos por fecha del último mensaje (más reciente primero)
    return sorted(chats_data, 
                 key=lambda x: x['last_message'].created_at if x['last_message'] else chat.created_at,
                 reverse=True)

def mark_messages_as_read(user: User, chat: Chat):
    """
    Marca como leídos todos los mensajes del chat que no sean del usuario.
    """
    Message.objects.filter(
        chat=chat,
        is_read=False
    ).exclude(
        sender=user
    ).update(is_read=True)
    
    update_last_activity(user)

def get_unread_messages_count(user: User) -> int:
    """
    Obtiene el número total de mensajes no leídos para un usuario.
    """
    user_chats = Chat.objects.filter(participants=user).values_list('id', flat=True)
    
    return Message.objects.filter(
        chat_id__in=user_chats,
        is_read=False
    ).exclude(
        sender=user
    ).count()