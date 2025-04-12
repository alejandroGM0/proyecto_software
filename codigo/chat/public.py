# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
API pública para la aplicación de chat.
"""
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count
from django.db.models import Count, Max, Subquery, OuterRef, F

from .models import Chat, Message
from accounts.public import update_last_activity

def get_messages_count():
    """
    Obtiene el número total de mensajes en el sistema.
    """
    return Message.objects.count()

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
    
    user_chats = Chat.objects.filter(participants=user).distinct()
    
    chats_data = []
    for chat in user_chats:
        last_message = chat.messages.order_by('-created_at').first()
        
        data = {
            'chat': chat,
            'last_message': last_message,
            'is_ride_chat': hasattr(chat, 'ride')
        }
        
        
        if hasattr(chat, 'ride'):
            data['ride'] = chat.ride
            
        chats_data.append(data)
    
    
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

def get_messages_in_period(start_date, end_date):
    """
    Obtiene el número de mensajes enviados en un periodo determinado
    """
    return Message.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).count()

def get_all_chats_with_stats():
    """
    Obtiene todos los chats del sistema con estadísticas útiles para el panel de administración.
    """
    chats = Chat.objects.all()
    chats_data = []
    
    for chat in chats:
        messages_count = chat.messages.count()
        last_message = chat.messages.order_by('-created_at').first()
        participants_count = chat.participants.count()
        
        chats_data.append({
            'chat': chat,
            'messages_count': messages_count,
            'last_message': last_message,
            'participants_count': participants_count,
            'is_ride_chat': hasattr(chat, 'ride')
        })
    
    return sorted(chats_data, 
                 key=lambda x: x['last_message'].created_at if x['last_message'] else chat.created_at,
                 reverse=True)

def filter_chats_by_criteria(search=None, chat_type=None, from_date=None, to_date=None):
    """
    Filtra los chats según los criterios especificados.
    """
    chats = Chat.objects.all()
    
    
    if search:
        
        matching_users = User.objects.filter(username__icontains=search)
        
        
        chats = chats.filter(participants__in=matching_users).distinct()
    
    
    if chat_type == 'ride':
        
        chats = chats.filter(ride__isnull=False)
    elif chat_type == 'direct':
        
        chats = chats.filter(ride__isnull=True)
    
    
    if from_date:
        chats = chats.filter(created_at__gte=from_date)
    if to_date:
        chats = chats.filter(created_at__lte=to_date)
    
    
    result = []
    for chat in chats:
        messages_count = chat.messages.count()
        last_message = chat.messages.order_by('-created_at').first()
        participants_count = chat.participants.count()
        
        result.append({
            'chat': chat,
            'messages_count': messages_count,
            'last_message': last_message,
            'participants_count': participants_count,
            'is_ride_chat': hasattr(chat, 'ride')
        })
    
    
    return sorted(result, 
                key=lambda x: x['last_message'].created_at if x['last_message'] else chat.created_at,
                reverse=True)

def filter_chats_by_criteria_optimized(search=None, chat_type=None, from_date=None, to_date=None):
    """
    Versión optimizada de filter_chats_by_criteria que no carga todos los mensajes
    sino solo datos esenciales para mostrar en la lista.
    """    
    
    chats_query = Chat.objects.all()
    
    
    if search:
        matching_users = User.objects.filter(username__icontains=search)
        chats_query = chats_query.filter(participants__in=matching_users).distinct()
    
    
    if chat_type == 'ride':
        chats_query = chats_query.filter(ride__isnull=False)
    elif chat_type == 'direct':
        chats_query = chats_query.filter(ride__isnull=True)
    
    
    if from_date:
        chats_query = chats_query.filter(created_at__gte=from_date)
    if to_date:
        chats_query = chats_query.filter(created_at__lte=to_date)
    
    
    chats_query = chats_query.annotate(
        messages_count=Count('messages', distinct=True),
        has_ride=Count('ride', distinct=True)
    )
    
    
    last_message_subquery = Message.objects.filter(
        chat=OuterRef('pk')
    ).order_by('-created_at').values('id', 'created_at')[:1]
    
    chats_query = chats_query.annotate(
        last_message_id=Subquery(last_message_subquery.values('id')),
        last_message_date=Subquery(last_message_subquery.values('created_at'))
    )
    
    
    chats_query = chats_query.order_by('-last_message_date', '-created_at')
    
    
    result = []
    for chat in chats_query:
        
        last_message = None
        if chat.last_message_id:
            last_message = Message.objects.get(id=chat.last_message_id)
        
        result.append({
            'chat': chat,
            'messages_count': chat.messages_count,
            'last_message': last_message,
            'is_ride_chat': chat.has_ride > 0
        })
    
    return result

def get_chat_stats():
    """
    Obtiene estadísticas generales sobre los chats para el panel de administración.
    """
    total_chats = Chat.objects.count()
    total_messages = Message.objects.count()
    ride_chats = Chat.objects.filter(ride__isnull=False).count()
    direct_chats = total_chats - ride_chats
    
    
    active_chats = Chat.objects.annotate(message_count=Count('messages'))\
                              .order_by('-message_count')[:5]
    
    active_chats_data = []
    for chat in active_chats:
        participants = ", ".join(user.username for user in chat.participants.all()[:3])
        if chat.participants.count() > 3:
            participants += "..."
            
        active_chats_data.append({
            'chat': chat,
            'participants': participants,
            'message_count': chat.message_count,
            'is_ride_chat': hasattr(chat, 'ride')
        })
    
    
    today = timezone.now().date()
    week_ago = today - timezone.timedelta(days=7)
    
    daily_messages = []
    for i in range(7):
        date = week_ago + timezone.timedelta(days=i)
        count = Message.objects.filter(
            created_at__date=date
        ).count()
        daily_messages.append({
            'date': date.strftime('%d/%m'),
            'count': count
        })
    
    return {
        'total_chats': total_chats,
        'total_messages': total_messages,
        'ride_chats': ride_chats,
        'direct_chats': direct_chats,
        'active_chats': active_chats_data,
        'daily_messages': daily_messages
    }

def delete_chat(chat_id):
    """
    Elimina un chat y todos sus mensajes.
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        chat.delete()
        return True
    except Chat.DoesNotExist:
        return False