from django.contrib import admin
from .models import Message, Chat
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

class ChatFilter(admin.SimpleListFilter):
    title = 'Tipo de Chat'
    parameter_name = 'chat_type'
    
    def lookups(self, request, model_admin):
        return [
            ('ride', 'Chats de Viaje'),
            ('direct', 'Chats Directos'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'ride':
            return queryset.filter(ride__isnull=False)
        if self.value() == 'direct':
            return queryset.filter(ride__isnull=True)
        return queryset

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at', 'has_ride')
    list_filter = (ChatFilter, 'created_at')
    search_fields = ('participants__username',)
    filter_horizontal = ('participants',)
    
    def get_participants(self, obj):
        return ", ".join(user.username for user in obj.participants.all()[:3])
    get_participants.short_description = 'Participantes'
    
    def has_ride(self, obj):
        return hasattr(obj, 'ride') and obj.ride is not None
    has_ride.boolean = True
    has_ride.short_description = 'Chat de Viaje'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('get_chat_info', 'sender', 'short_content', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'sender', ChatFilter)
    list_display_links = ('get_chat_info', 'short_content')
    search_fields = ('content', 'sender__username', 'chat__participants__username')
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Mensaje'
    
    def get_chat_info(self, obj):
        if hasattr(obj.chat, 'ride') and obj.chat.ride:
            ride = obj.chat.ride
            return f"Viaje: {ride.origin} → {ride.destination}"
        return f"Directo: {', '.join(user.username for user in obj.chat.participants.all()[:3])}"
    get_chat_info.short_description = 'Chat'
