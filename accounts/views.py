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

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect('rides:ride_list')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

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
            messages.success(request, 'Registro exitoso!')
            return redirect('rides:ride_list')
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'accounts/register.html', {
        'user_form': user_form, 
        'profile_form': profile_form
    })

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('rides:ride_list')

@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = profile_user.profile
    
    if not user_profile.profile_visible and request.user.id != user_id:
        messages.error(request, 'Este perfil es privado.')
        return redirect('rides:ride_list')
    
    rides_as_driver = Ride.objects.filter(driver=profile_user)
    rides_as_passenger = profile_user.rides_as_passenger.all()
    
    active_rides_as_driver = rides_as_driver.filter(departure_time__gt=timezone.now())
    past_rides_as_driver = rides_as_driver.filter(departure_time__lte=timezone.now())
    
    if not user_profile.show_rides_history and request.user.id != user_id:
        active_rides_as_driver = active_rides_as_driver.none()
        past_rides_as_driver = past_rides_as_driver.none()
        rides_as_passenger = rides_as_passenger.none()
    
    context = {
        'user': profile_user,
        'user_profile': user_profile,
        'active_rides_as_driver': active_rides_as_driver,
        'past_rides_as_driver': past_rides_as_driver,
        'rides_as_passenger': rides_as_passenger,
        'total_rides': rides_as_driver.count() + rides_as_passenger.count(),
        'is_own_profile': request.user.id == user_id
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile(request):
    return user_profile(request, request.user.id)

@login_required
def settings_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        settings_type = request.POST.get('settings_type')
        
        if settings_type == 'account':
            username = request.POST.get('username')
            email = request.POST.get('email')
            
            if username and username != request.user.username:
                request.user.username = username
            
            if email:
                request.user.email = email
            
            request.user.save()
            messages.success(request, 'Información de cuenta actualizada correctamente.')
        
        elif settings_type == 'profile':
            if 'profile_image' in request.FILES:
                user_profile.profile_image = request.FILES['profile_image']
            
            profile_data = {
                'bio': request.POST.get('bio', ''),
                'phone_number': request.POST.get('phone_number', ''),
                'location': request.POST.get('location', ''),
                'birth_date': request.POST.get('birth_date', None),
            }
            
            profile_data = {k: v for k, v in profile_data.items() if v}
            
            for field, value in profile_data.items():
                setattr(user_profile, field, value)
            user_profile.save()
            messages.success(request, 'Información personal actualizada correctamente.')
            
        elif settings_type == 'vehicle':
            user_profile.has_vehicle = 'has_vehicle' in request.POST
            
            if user_profile.has_vehicle:
                user_profile.vehicle_model = request.POST.get('vehicle_model', '')
                user_profile.vehicle_year = request.POST.get('vehicle_year') or None
                user_profile.vehicle_color = request.POST.get('vehicle_color', '')
                user_profile.vehicle_features = request.POST.get('vehicle_features', '')
            
            user_profile.save()
            messages.success(request, 'Información del vehículo actualizada correctamente.')
            
        elif settings_type == 'preferences':
            user_profile.pref_music = request.POST.get('pref_music', user_profile.pref_music)
            user_profile.pref_talk = request.POST.get('pref_talk', user_profile.pref_talk)
            user_profile.pref_pets = 'pref_pets' in request.POST
            user_profile.pref_smoking = 'pref_smoking' in request.POST
            
            user_profile.save()
            messages.success(request, 'Preferencias de viaje actualizadas correctamente.')
            
        elif settings_type == 'notifications':
            user_profile.email_notifications = 'email_notifications' in request.POST
            user_profile.message_notifications = 'message_notifications' in request.POST
            user_profile.ride_notifications = 'ride_notifications' in request.POST
            user_profile.save()
            messages.success(request, 'Preferencias de notificaciones actualizadas.')
            
        elif settings_type == 'privacy':
            user_profile.profile_visible = 'profile_visible' in request.POST
            user_profile.show_rides_history = 'show_rides_history' in request.POST
            user_profile.save()
            messages.success(request, 'Preferencias de privacidad actualizadas.')
    
    profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'user_profile': user_profile,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/settings.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('accounts:settings')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})