from django.shortcuts import render
from .models import Ride

def ride_list(request):
    rides = Ride.objects.all()
    return render(request, 'rides/ride_list.html', {'rides': rides})
