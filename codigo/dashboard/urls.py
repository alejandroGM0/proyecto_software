# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.urls import path
from . import views
from .constants import (
    URL_DASHBOARD, URL_TRIP_STATS, URL_MSG_STATS,
    URL_REPORT_STATS, URL_USER_STATS, URL_RIDE_MANAGEMENT,
    URL_USER_MANAGEMENT, URL_CHAT_MANAGEMENT
)

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('trips/', views.trip_stats, name='trip_stats'),
    path('messages/', views.message_stats, name='msg_stats'),
    path('reports/', views.report_stats, name='report_stats'),
    path('users/', views.user_stats, name='user_stats'),
    path('ride-management/', views.ride_management, name='ride_management'),
    path('user-management/', views.user_management, name='user_management'),
    path('chat-management/', views.chat_management, name='chat_management'),
    
    path('api/trips/', views.get_trip_data_json, name='get_trip_data_json'),
    path('api/messages/', views.get_message_data_json, name='get_message_data_json'),
    path('api/reports/', views.get_report_data_json, name='get_report_data_json'),
    path('api/users/', views.get_user_data_json, name='get_user_data_json'),
    path('api/payments/', views.get_payment_data_json, name='get_payment_data_json'),
    path('api/data/', views.dashboard_data_api, name='dashboard_data_api'),
    path('api/chat/<int:chat_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('mark-report/<int:pk>/', views.mark_report, name='mark_report'),
]
