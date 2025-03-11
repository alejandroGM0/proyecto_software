from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from rides.models import Ride
from .models import Message
from django.contrib import messages
from .utils import user_has_chat_access, get_user_chats
from chat import models

@login_required
def ride_chat(request, ride_id=None):
    chats_data = get_user_chats(request.user)
    
    selected_ride = None
    if ride_id:
        selected_ride = get_object_or_404(Ride, id=ride_id)
        if not user_has_chat_access(request.user, selected_ride):
            messages.error(request, 'No tienes permiso para acceder a este chat.')
            return redirect('rides:ride_list')
    
    return render(request, 'chat/chat.html', {
        'chats_data': chats_data,
        'selected_ride': selected_ride
    })

@login_required
def get_messages(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    
    if not user_has_chat_access(request.user, ride):
        return HttpResponseForbidden('No tienes permiso para acceder a este chat')
    
    messages = ride.messages.all()
    messages_data = [{
        'content': msg.content,
        'sender': msg.sender.username,
        'timestamp': msg.created_at.strftime('%H:%M')
    } for msg in messages]
    
    return JsonResponse({
        'messages': messages_data,
        'is_active': ride.is_active
    })

@login_required
def my_chats(request):
    user_rides = Ride.objects.filter(
        models.Q(driver=request.user) | 
        models.Q(passengers=request.user)
    ).distinct()
    
    chats_data = []
    for ride in user_rides:
        last_message = ride.messages.order_by('-created_at').first()
        unread_count = ride.messages.filter(is_read=False).exclude(sender=request.user).count()
        
        chats_data.append({
            'ride': ride,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    return render(request, 'chat/my_chats.html', {
        'chats_data': chats_data
    })
