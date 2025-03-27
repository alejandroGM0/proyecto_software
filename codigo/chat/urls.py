from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.my_chats, name='my_chats'),
    path('<int:chat_id>/', views.chat_view, name='chat_view'),
    path('ride/<int:ride_id>/', views.chat_view, name='ride_chat'),
    path('<int:chat_id>/messages/', views.get_messages, name='get_messages'),
    path('new/<int:user_id>/', views.create_direct_chat, name='create_direct_chat'),
]