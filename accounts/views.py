from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rides.models import Ride
from django.utils import timezone

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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro exitoso!')
            return redirect('rides:ride_list')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('rides:ride_list')

@login_required
def profile(request):
    user = request.user
    rides_as_driver = Ride.objects.filter(driver=user)
    rides_as_passenger = user.rides_as_passenger.all()
    
    active_rides_as_driver = rides_as_driver.filter(departure_time__gt=timezone.now())
    past_rides_as_driver = rides_as_driver.filter(departure_time__lte=timezone.now())
    
    context = {
        'user': user,
        'active_rides_as_driver': active_rides_as_driver,
        'past_rides_as_driver': past_rides_as_driver,
        'rides_as_passenger': rides_as_passenger,
        'total_rides': rides_as_driver.count() + rides_as_passenger.count()
    }
    return render(request, 'accounts/profile.html', context)
