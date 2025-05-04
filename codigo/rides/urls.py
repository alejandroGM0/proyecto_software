# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
URL configuration for blablacar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'rides'

urlpatterns = [
    path('', views.ride_list, name='ride_list'),  # Página principal
    path('search/', views.search_ride, name='search_ride'),  
    path('book/<int:ride_id>/', views.book_ride, name='book_ride'),
    path('ride/<int:ride_id>/', views.ride_detail, name='ride_detail'),
    path('ride/create/', views.create_ride, name='create_ride'),
    path('ride/<int:ride_id>/edit/', views.edit_ride, name='edit_ride'),
    path('cancel-booking/<int:ride_id>/', views.cancel_booking, name='cancel_booking'),
]
