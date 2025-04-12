# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
from django.core.management.base import BaseCommand
from rides.models import Ride
from chat._utils import synchronize_chat_participants 

class Command(BaseCommand):
    help = 'Sincroniza los participantes del chat con los viajes existentes'

    def handle(self, *args, **kwargs):
        rides = Ride.objects.all()
        count = 0
        
        for ride in rides:
            if hasattr(ride, 'chat') and ride.chat:
                before_count = ride.chat.participants.count()
                synchronize_chat_participants(ride)
                after_count = ride.chat.participants.count()
                
                if after_count > before_count:
                    count += 1
                    self.stdout.write(f"Sincronizado viaje {ride.id}: {before_count} → {after_count} participantes")
        
        self.stdout.write(self.style.SUCCESS(f'Sincronizados {count} chats'))