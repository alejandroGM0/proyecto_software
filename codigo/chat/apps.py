from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    
    def ready(self):
        print("¡ChatConfig.ready() llamado - cargando signals!")
        import chat.signals  # Importar señales cuando la app esté lista
