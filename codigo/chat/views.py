# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from rides.models import Ride
from .models import Message, Chat
from .public import user_has_chat_access, get_user_chats, mark_messages_as_read
from ._utils import get_messages_for_chat, can_send_message
from accounts.public import update_last_activity
from .constants import (
    TEMPLATE_CHAT, TEMPLATE_MY_CHATS,
    CONTEXT_CHATS_DATA, CONTEXT_SELECTED_CHAT, CONTEXT_SELECTED_RIDE,
    MESSAGE_NO_PERMISSION, URL_RIDES_LIST
)

@login_required
def chat_view(request, chat_id=None, ride_id=None):
    """
    Vista principal de chat. Puede accederse por chat_id o ride_id.
    """
    update_last_activity(request.user)
    chats_data = get_user_chats(request.user)
    
    selected_chat = None
    selected_ride = None
    
    # Si se proporciona un ID de viaje, obtenemos su chat
    if ride_id:
        ride = get_object_or_404(Ride, id=ride_id)
        if not hasattr(ride, 'chat'):
            messages.error(request, "Este viaje no tiene un chat asociado.")
            return redirect(URL_RIDES_LIST)
        
        selected_chat = ride.chat
        selected_ride = ride
        
        if not user_has_chat_access(request.user, selected_chat):
            messages.error(request, MESSAGE_NO_PERMISSION)
            return redirect(URL_RIDES_LIST)
    
    # Si se proporciona un ID de chat, lo usamos directamente
    elif chat_id:
        selected_chat = get_object_or_404(Chat, id=chat_id)
        
        if not user_has_chat_access(request.user, selected_chat):
            messages.error(request, MESSAGE_NO_PERMISSION)
            return redirect('chat:my_chats')
        
        # Si el chat tiene un viaje asociado, lo obtenemos
        if hasattr(selected_chat, 'ride'):
            selected_ride = selected_chat.ride
    
    # Si hay un chat seleccionado, marcamos sus mensajes como leídos
    if selected_chat:
        mark_messages_as_read(request.user, selected_chat)
    
    return render(request, TEMPLATE_CHAT, {
        CONTEXT_CHATS_DATA: chats_data,
        CONTEXT_SELECTED_CHAT: selected_chat,
        CONTEXT_SELECTED_RIDE: selected_ride,
    })

@login_required
def get_messages(request, chat_id):
    """
    Devuelve los mensajes de un chat en formato JSON.
    """
    update_last_activity(request.user)
    chat = get_object_or_404(Chat, id=chat_id)
    
    if not user_has_chat_access(request.user, chat):
        return HttpResponseForbidden(MESSAGE_NO_PERMISSION)
    
    # Marcar mensajes como leídos
    mark_messages_as_read(request.user, chat)
    
    messages_data = get_messages_for_chat(chat)
    
    return JsonResponse({
        'messages': messages_data,
        'is_active': can_send_message(chat),
        'is_ride_chat': hasattr(chat, 'ride')
    })

@login_required
def my_chats(request):
    """
    Vista para mostrar todos los chats del usuario.
    """
    update_last_activity(request.user)
    chats_data = get_user_chats(request.user)
    
    return render(request, TEMPLATE_MY_CHATS, {
        CONTEXT_CHATS_DATA: chats_data,
        # Añadir este contexto para que la plantilla sepa que estamos en la vista de todos los chats
        'is_chats_page': True
    })

@login_required
def create_direct_chat(request, user_id):
    """
    Crea o accede a un chat directo con otro usuario.
    """
    from django.contrib.auth.models import User
    
    other_user = get_object_or_404(User, id=user_id)
    
    # No permitir chat con uno mismo
    if request.user == other_user:
        messages.error(request, "No puedes chatear contigo mismo.")
        return redirect('chat:my_chats')
    
    # Buscar si ya existe un chat directo entre estos usuarios
    # (Un chat directo es entre exactamente 2 usuarios y no está asociado a un viaje)
    user_chats = Chat.objects.filter(
        participants=request.user,
        ride__isnull=True
    ).filter(
        participants=other_user
    )
    
    # Filtrar para encontrar chats con exactamente 2 participantes
    for chat in user_chats:
        if chat.participants.count() == 2:
            return redirect('chat:chat_view', chat_id=chat.id)
    
    # Si no existe, crear un nuevo chat directo
    new_chat = Chat.objects.create()
    new_chat.participants.add(request.user, other_user)
    
    return redirect('chat:chat_view', chat_id=new_chat.id)
