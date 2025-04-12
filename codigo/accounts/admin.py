# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil de usuario'
    fieldsets = [
        ('Información personal', {
            'fields': ['bio', 'phone_number', 'location', 'birth_date'],
        }),
        ('Vehículo', {
            'fields': ['has_vehicle', 'vehicle_model', 'vehicle_year', 'vehicle_color', 'vehicle_features'],
            'classes': ['collapse'],
        }),
        ('Preferencias de viaje', {
            'fields': ['pref_music', 'pref_talk', 'pref_pets', 'pref_smoking'],
            'classes': ['collapse'],
        }),
        ('Notificaciones', {
            'fields': ['email_notifications', 'message_notifications', 'ride_notifications'],
            'classes': ['collapse'],
        }),
        ('Privacidad', {
            'fields': ['profile_visible', 'show_rides_history'],
            'classes': ['collapse'],
        }),
    ]

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'get_location', 'get_vehicle')
    list_filter = ('is_active', 'is_staff', 'profile__has_vehicle')
    search_fields = ('username', 'email', 'profile__location')
    
    def get_location(self, obj):
        return obj.profile.location if hasattr(obj, 'profile') else "-"
    get_location.short_description = 'Ubicación'
    
    def get_vehicle(self, obj):
        if hasattr(obj, 'profile'):
            return f"{obj.profile.vehicle_model} ({obj.profile.vehicle_year})" if obj.profile.has_vehicle else "No"
        return "-"
    get_vehicle.short_description = 'Vehículo'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'has_vehicle', 'vehicle_model', 'last_active')
    list_filter = ('has_vehicle', 'pref_music', 'pref_talk', 'pref_pets', 'pref_smoking')
    search_fields = ('user__username', 'location', 'vehicle_model')
    fieldsets = [
        ('Usuario', {
            'fields': ['user'],
        }),
        ('Información personal', {
            'fields': ['bio', 'phone_number', 'location', 'birth_date'],
        }),
        ('Vehículo', {
            'fields': ['has_vehicle', 'vehicle_model', 'vehicle_year', 'vehicle_color', 'vehicle_features'],
        }),
        ('Preferencias de viaje', {
            'fields': ['pref_music', 'pref_talk', 'pref_pets', 'pref_smoking'],
        }),
        ('Notificaciones', {
            'fields': ['email_notifications', 'message_notifications', 'ride_notifications'],
        }),
        ('Privacidad', {
            'fields': ['profile_visible', 'show_rides_history'],
        }),
        ('Actividad', {
            'fields': ['last_active'],
            'classes': ['collapse'],
        }),
    ]
    readonly_fields = ('last_active',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)