from django.contrib import admin
from .models import Ride

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("driver", "origin", "destination", "departure_time", "seats_available")
    filter_horizontal = ('passengers',)  # Añade una interfaz mejor para gestionar pasajeros
