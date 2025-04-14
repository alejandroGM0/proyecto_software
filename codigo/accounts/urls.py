# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.urls import path
from . import views
from .constants import *

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),  # Redirige al perfil del usuario logueado
    path('profile/<str:username>/', views.profile_view, name='profile_view'),  # Cambiado de user_id a username
    path('settings/', views.settings_view, name='settings'),
    path('change-password/', views.change_password, name='change_password'),
    path('setup-payment-account/', views.setup_payment_account, name='setup_payment_account'),
    path('complete-stripe-onboarding/', views.complete_stripe_onboarding, name='complete_stripe_onboarding'),
]