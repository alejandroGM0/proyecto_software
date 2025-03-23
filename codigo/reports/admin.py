from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'importance', 'user', 'created_at', 'read', 'has_response')
    list_filter = ('report_type', 'importance', 'read', 'created_at')
    search_fields = ('title', 'description', 'response')
    date_hierarchy = 'created_at'
    list_editable = ('read',)
    actions = ['mark_as_read', 'mark_as_unread']
    
    fieldsets = [
        ('Información básica', {
            'fields': ['title', 'description', 'report_type', 'importance', 'user', 'read']
        }),
        ('Respuesta', {
            'fields': ['response', 'response_by', 'response_at']
        }),
    ]
    
    def has_response(self, obj):
        return bool(obj.response)
    has_response.boolean = True
    has_response.short_description = "Respondido"
    
    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
        self.message_user(request, f"{queryset.count()} reportes marcados como leídos.")
    mark_as_read.short_description = "Marcar como leídos"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
        self.message_user(request, f"{queryset.count()} reportes marcados como no leídos.")
    mark_as_unread.short_description = "Marcar como no leídos"
