from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from rides.models import Ride
from .models import Message
from .public import user_has_chat_access, get_user_chats
from ._utils import get_messages_for_ride, can_send_message
from accounts.public import update_last_activity
from .constants import (
    TEMPLATE_CHAT, TEMPLATE_MY_CHATS,
    CONTEXT_CHATS_DATA, CONTEXT_SELECTED_RIDE,
    MESSAGE_NO_PERMISSION, URL_RIDES_LIST
)

@login_required
def ride_chat(request, ride_id=None):
    update_last_activity(request.user)
    chats_data = get_user_chats(request.user)
    
    selected_ride = None
    if ride_id:
        selected_ride = get_object_or_404(Ride, id=ride_id)
        if not user_has_chat_access(request.user, selected_ride):
            messages.error(request, MESSAGE_NO_PERMISSION)
            return redirect(URL_RIDES_LIST)
    
    return render(request, TEMPLATE_CHAT, {
        CONTEXT_CHATS_DATA: chats_data,
        CONTEXT_SELECTED_RIDE: selected_ride
    })

@login_required
def get_messages(request, ride_id):
    update_last_activity(request.user)
    ride = get_object_or_404(Ride, id=ride_id)
    
    if not user_has_chat_access(request.user, ride):
        return HttpResponseForbidden(MESSAGE_NO_PERMISSION)
    
    messages_data = get_messages_for_ride(ride)
    
    return JsonResponse({
        'messages': messages_data,
        'is_active': can_send_message(ride)
    })

@login_required
def my_chats(request):
    update_last_activity(request.user)
    chats_data = get_user_chats(request.user)
    
    return render(request, TEMPLATE_MY_CHATS, {
        CONTEXT_CHATS_DATA: chats_data
    })
