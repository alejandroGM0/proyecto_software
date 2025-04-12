# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from rides.models import Ride
from django.utils import timezone
from .forms import CustomUserCreationForm, UserProfileForm
from .models import UserProfile
from .public import (
    get_user_profile, get_user_by_username, update_last_activity
)
from .constants import *
from ._utils import *
from django.core.paginator import Paginator

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get(USERNAME_FIELD)
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, LOGIN_SUCCESS.format(username))
                return redirect(RIDE_LIST_URL)
    else:
        form = AuthenticationForm()
    return render(request, LOGIN_TEMPLATE, {FORM_KEY: form})

def register_view(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            messages.success(request, REGISTRATION_SUCCESS)
            return redirect(RIDE_LIST_URL)
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    
    return render(request, REGISTER_TEMPLATE, {
        USER_FORM_KEY: user_form, 
        PROFILE_FORM_KEY: profile_form
    })

def logout_view(request):
    logout(request)
    messages.info(request, LOGOUT_SUCCESS)
    return redirect(RIDE_LIST_URL)

@login_required
def profile_view(request, username):
    user, user_profile = get_user_and_profile(request, username)
    #Necesario en caso de buscar el perfil de otro usuario (no necesariamente el mismo que esta logueado)
    if not user:
        return redirect(RIDE_LIST_URL)
    
    # Primero obtenemos los datos de viajes
    rides_data = get_user_rides_data(user)
    profile_data = get_user_profile_data(user)
    
    # Extraemos las listas de viajes de rides_data
    active_rides_as_driver = rides_data.get('active_rides_as_driver', [])
    expired_rides_as_driver = rides_data.get('expired_rides_as_driver', [])
    active_rides_as_passenger = rides_data.get('active_rides_as_passenger', [])
    expired_rides_as_passenger = rides_data.get('expired_rides_as_passenger', [])
    
    # Ahora creamos los paginadores con las listas obtenidas
    # Paginación para viajes como conductor (activos)
    paginator_driver_active = Paginator(active_rides_as_driver, 6)
    driver_active_page = request.GET.get('page') if request.GET.get('tab') == 'driver' and request.GET.get('status') == 'active' else 1
    active_driver_page_obj = paginator_driver_active.get_page(driver_active_page)
    
    # Paginación para viajes como conductor (finalizados)
    paginator_driver_expired = Paginator(expired_rides_as_driver, 6)
    driver_expired_page = request.GET.get('page') if request.GET.get('tab') == 'driver' and request.GET.get('status') == 'expired' else 1
    expired_driver_page_obj = paginator_driver_expired.get_page(driver_expired_page)
    
    # Paginación para viajes como pasajero (activos)
    paginator_passenger_active = Paginator(active_rides_as_passenger, 6)
    passenger_active_page = request.GET.get('page') if request.GET.get('tab') == 'passenger' and request.GET.get('status') == 'active' else 1
    active_passenger_page_obj = paginator_passenger_active.get_page(passenger_active_page)
    
    # Paginación para viajes como pasajero (finalizados)
    paginator_passenger_expired = Paginator(expired_rides_as_passenger, 6)
    passenger_expired_page = request.GET.get('page') if request.GET.get('tab') == 'passenger' and request.GET.get('status') == 'expired' else 1
    expired_passenger_page_obj = paginator_passenger_expired.get_page(passenger_expired_page)
    
    # También necesitamos modificar el contexto para mostrar las versiones paginadas
    context = {
        USER_KEY: user,
        USER_PROFILE_KEY: user_profile,
        IS_OWN_PROFILE_KEY: request.user == user,
        # Incluimos los datos originales para mantener la compatibilidad con código existente
        **rides_data,
        **profile_data,
        # Añadimos los objetos de paginación
        'active_driver_page_obj': active_driver_page_obj,
        'expired_driver_page_obj': expired_driver_page_obj,
        'active_passenger_page_obj': active_passenger_page_obj,
        'expired_passenger_page_obj': expired_passenger_page_obj,
    }
    
    return render(request, PROFILE_TEMPLATE, context)

@login_required
def profile(request):
    return redirect(PROFILE_VIEW_URL, username=request.user.username)

@login_required
def settings_view(request):
    user_profile = get_user_profile(request.user)
    update_last_activity(request.user)
    settings_type = request.POST.get('settings_type')
    
    if request.method == 'POST':
            if settings_type == ACCOUNT_SETTINGS:
                update_account_settings(request)
            elif settings_type == PROFILE_SETTINGS:
                update_profile_settings(request, user_profile)
            elif settings_type == VEHICLE_SETTINGS:
                update_vehicle_settings(request, user_profile)
            elif settings_type == PREFERENCES_SETTINGS:
                update_preferences_settings(request, user_profile)
            elif settings_type == NOTIFICATIONS_SETTINGS:
                update_notification_settings(request, user_profile)
            elif settings_type == PRIVACY_SETTINGS:
                update_privacy_settings(request, user_profile)
        
    context = get_settings_context(request.user, user_profile)
    return render(request, SETTINGS_TEMPLATE, context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, PASSWORD_UPDATE_SUCCESS)
            return redirect(SETTINGS_URL)
        else:
            messages.error(request, FORM_ERROR)
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, CHANGE_PASSWORD_TEMPLATE, {FORM_KEY: form})