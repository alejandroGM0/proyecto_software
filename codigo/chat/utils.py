from django.contrib.auth.models import User
from rides.models import Ride
from django.db import models

def user_has_chat_access(user: User, ride: Ride) -> bool:
    return user == ride.driver or user in ride.passengers.all()

def get_user_chats(user: User):
    user_rides = Ride.objects.filter(
        models.Q(driver=user) | 
        models.Q(passengers=user)
    ).distinct()
    
    chats_data = []
    for ride in user_rides:
        last_message = ride.messages.order_by('-created_at').first()
        
        chats_data.append({
            'ride': ride,
            'last_message': last_message
        })
    
    return chats_data