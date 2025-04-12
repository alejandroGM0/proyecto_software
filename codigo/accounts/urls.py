# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),  # Redirige al perfil del usuario logueado
    path('profile/<str:username>/', views.profile_view, name='profile_view'),  # Cambiado de user_id a username
    path('settings/', views.settings_view, name='settings'),
    path('change-password/', views.change_password, name='change_password'),
]