import logging
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from rides.models import Ride
from .models import Chat

# Configuramos el logger para depuración
logger = logging.getLogger(__name__)
print("¡CHAT SIGNALS IMPORTADO!")  # Esta línea se ejecutará al importar el módulo

#TODO RECORDAR ELIMINAR LOS LOGGING ANTES DE DESPLEGAR
@receiver(post_save, sender=Ride)
def create_chat_for_ride(sender, instance, created, **kwargs):
    """Crea un chat automáticamente cuando se crea un viaje"""
    print(f"Signal create_chat_for_ride llamado para viaje {instance.id}, created={created}")
    
    if created and (not hasattr(instance, 'chat') or instance.chat is None):
        print(f"Creando nuevo chat para viaje {instance.id}")
        chat = Chat.objects.create()
        chat.participants.add(instance.driver)
        print(f"Añadido conductor {instance.driver.username} al chat")
        
        Ride.objects.filter(id=instance.id).update(chat=chat)
        print(f"Chat {chat.id} asociado al viaje {instance.id}")
    else:
        if hasattr(instance, 'chat') and instance.chat is not None:
            print(f"El viaje {instance.id} ya tiene chat {instance.chat.id}")
        else:
            print(f"El viaje {instance.id} no tiene chat pero no se crea uno porque condición falló")

@receiver(m2m_changed, sender=Ride.passengers.through)
def update_chat_participants(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Añade pasajeros al chat cuando se añaden al viaje"""
    print(f"Signal update_chat_participants llamado para viaje {instance.id}, action={action}")
    
    if action == "post_add" and hasattr(instance, 'chat') and instance.chat:
        print(f"Añadiendo pasajeros al chat del viaje {instance.id}")
        for user_id in pk_set:
            user = model.objects.get(id=user_id)
            instance.chat.participants.add(user)
            print(f"Añadido pasajero {user.username} al chat del viaje {instance.id}")
    else:
        if not hasattr(instance, 'chat'):
            print(f"ERROR: El viaje {instance.id} no tiene atributo 'chat'")
        elif not instance.chat:
            print(f"ERROR: El chat del viaje {instance.id} es None")