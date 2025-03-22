from django.contrib import admin
from .models import Message
from rides.models import Ride

class RideChatFilter(admin.SimpleListFilter):
    title = 'Conversación'
    parameter_name = 'chat'
    
    def lookups(self, request, model_admin):
        rides_with_messages = Ride.objects.filter(messages__isnull=False).distinct()
        return [(ride.id, f"{ride.origin} → {ride.destination}") for ride in rides_with_messages]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ride__id=self.value())
        return queryset

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('get_ride_info', 'sender', 'short_content', 'created_at', 'is_read')
    list_filter = (RideChatFilter, 'is_read', 'created_at', 'sender')
    list_display_links = ('get_ride_info', 'short_content')
    search_fields = ('content', 'sender__username', 'ride__origin', 'ride__destination')
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Mensaje'
    
    def get_ride_info(self, obj):
        if hasattr(obj, 'ride') and obj.ride:
            return f"{obj.ride.origin} → {obj.ride.destination}"
        return "Sin viaje asociado"
    get_ride_info.short_description = 'Conversación'
    
    fieldsets = (
        ('Información del Mensaje', {
            'fields': ('content', 'is_read')
        }),
        ('Relaciones', {
            'fields': ('ride', 'sender')
        }),
        ('Información Temporal', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
