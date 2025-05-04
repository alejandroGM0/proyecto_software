# ==========================================
# Autor: David Colás Martín
# ==========================================
from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payer", "recipient", "amount", "status", "created_at")
    list_filter = ("status", "payment_method")
    search_fields = ("payer__username", "recipient__username", "transaction_id")
    date_hierarchy = "created_at"
