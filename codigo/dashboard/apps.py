# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    verbose_name = 'Panel de Control'
