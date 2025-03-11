from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ride_chat, name='my_chats'),
    path('<int:ride_id>/', views.ride_chat, name='ride_chat'),
    path('<int:ride_id>/messages/', views.get_messages, name='get_messages'),
]