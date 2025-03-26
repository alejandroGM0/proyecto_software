"""
API pública de la aplicación de chat.
"""
from django.contrib.auth.models import User
from .models import Message
from rides.models import Ride
from accounts.public import update_last_activity

def user_has_chat_access(user: User, ride: Ride) -> bool:
    """
    Verifica si un usuario tiene acceso al chat de un viaje.
    """
    return user == ride.driver or user in ride.passengers.all()

def get_user_chats(user: User):
    """
    Obtiene todos los chats en los que participa un usuario.
    """
    from django.db.models import Q
    
    user_rides = Ride.objects.filter(
        Q(driver=user) | 
        Q(passengers=user)
    ).distinct()
    
    chats_data = []
    for ride in user_rides:
        last_message = ride.messages.order_by('-created_at').first()
        
        chats_data.append({
            'ride': ride,
            'last_message': last_message
        })
    
    return chats_data

def mark_messages_as_read(user: User, ride: Ride):
    """
    Marca como leídos todos los mensajes del chat que no sean del usuario.
    """
    Message.objects.filter(
        ride=ride,
        is_read=False
    ).exclude(
        sender=user
    ).update(is_read=True)
    
    update_last_activity(user)

def get_unread_messages_count(user: User) -> int:
    """
    Obtiene el número total de mensajes no leídos para un usuario.
    """
    from django.db.models import Q
    
    user_rides = Ride.objects.filter(
        Q(driver=user) | 
        Q(passengers=user)
    ).values_list('id', flat=True)
    
    return Message.objects.filter(
        ride_id__in=user_rides,
        is_read=False
    ).exclude(
        sender=user
    ).count()