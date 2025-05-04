# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================



import random
import string
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction

from accounts.models import UserProfile
from rides.models import Ride
from chat.models import Chat, Message
from reports.models import Report
from payments.models import Payment


class Command(BaseCommand):
    help = 'Genera datos de prueba para la aplicación'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=20, help='Número de usuarios a crear')
        parser.add_argument('--rides', type=int, default=50, help='Número de viajes a crear')
        parser.add_argument('--chats', type=int, default=30, help='Número de chats a crear')
        parser.add_argument('--messages', type=int, default=200, help='Número de mensajes a crear')
        parser.add_argument('--reports', type=int, default=25, help='Número de reportes a crear')
        parser.add_argument('--payments', type=int, default=40, help='Número de pagos a crear')
        parser.add_argument('--clean', action='store_true', help='Limpiar datos existentes antes de generar')

    def handle(self, *args, **options):
        if options['clean']:
            self.clean_database()
            self.stdout.write(self.style.SUCCESS('Base de datos limpiada exitosamente'))

        num_users = options['users']
        num_rides = options['rides']
        num_chats = options['chats']
        num_messages = options['messages']
        num_reports = options['reports']
        num_payments = options['payments']

        try:
            with transaction.atomic():
                
                users = self.create_users(num_users)
                self.stdout.write(self.style.SUCCESS(f'Creados {len(users)} usuarios'))

                
                rides = self.create_rides(users, num_rides)
                self.stdout.write(self.style.SUCCESS(f'Creados {len(rides)} viajes'))

                
                chats = self.create_chats(users, rides, num_chats)
                self.stdout.write(self.style.SUCCESS(f'Creados {len(chats)} chats'))
                
                messages = self.create_messages(chats, num_messages)
                self.stdout.write(self.style.SUCCESS(f'Creados {len(messages)} mensajes'))

                
                reports = self.create_reports(users, rides, num_reports)
                self.stdout.write(self.style.SUCCESS(f'Creados {len(reports)} reportes'))

                
                payments = self.create_payments(users, rides, num_payments)
                self.stdout.write(self.style.SUCCESS(f'Creados {len(payments)} pagos'))

            self.stdout.write(self.style.SUCCESS('Datos de prueba generados exitosamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al generar datos: {e}'))

    def clean_database(self):
        """Limpia los datos existentes en la base de datos."""
        
        Payment.objects.all().delete()
        Report.objects.all().delete()
        Message.objects.all().delete()
        Chat.objects.all().delete()
        Ride.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()  

    def create_users(self, count):
        """Crea usuarios de prueba con perfiles."""
        users = []
        existing_users = list(User.objects.all())
        
        
        if len(existing_users) >= count:
            return existing_users[:count]
        
        
        users.extend(existing_users)
        
        
        for i in range(len(existing_users) + 1, count + 1):
            username = f"user{i}"
            email = f"user{i}@example.com"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",
                first_name=random.choice(["Ana", "Luis", "María", "Pedro", "Juan", "Laura", "Carlos", "Elena", "Pablo", "Sofía"]),
                last_name=random.choice(["García", "Rodríguez", "López", "Martínez", "Fernández", "González", "Pérez", "Sánchez", "Romero", "Torres"]),
                date_joined=timezone.now() - timedelta(days=random.randint(1, 365))
            )
            
            
            has_vehicle = random.choice([True, False])
            location = random.choice(["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Málaga", "Alicante", "Murcia", "Granada", "Zaragoza"])
            
            UserProfile.objects.create(
                user=user,
                has_vehicle=has_vehicle,
                location=location,
                bio=f"Soy {user.first_name}, me gusta viajar y conocer gente nueva.",
                last_active=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            
            users.append(user)
        
        return users

    def create_rides(self, users, count):
        """Crea viajes de prueba."""
        rides = []
        
        
        cities = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Málaga", "Zaragoza", "Bilbao", 
                "Alicante", "Murcia", "Granada", "Palma", "Córdoba", "Valladolid", "Vigo", 
                "Gijón", "A Coruña", "Pamplona", "San Sebastián", "Santander", "Oviedo"]
        
        for _ in range(count):
            
            now = timezone.now()
            
            
            if random.random() < 0.7:  
                departure_time = now + timedelta(days=random.randint(1, 30))
            else:  
                departure_time = now - timedelta(days=random.randint(1, 30))
            
            
            origin = random.choice(cities)
            destination = random.choice([city for city in cities if city != origin])
            
            price = Decimal(str(round(random.uniform(5.0, 60.0), 2)))
            total_seats = random.randint(1, 4)
            
            
            drivers = [u for u in users if hasattr(u, 'userprofile') and u.userprofile.has_vehicle]
            if not drivers:
                
                driver = random.choice(users)
            else:
                driver = random.choice(drivers)
            
            
            ride = Ride.objects.create(
                driver=driver,
                origin=origin,
                destination=destination,
                departure_time=departure_time,
                price=price,
                total_seats=total_seats
            )
            
            
            available_passengers = [u for u in users if u != driver]
            
            
            target_available_seats = random.randint(0, total_seats)
            passengers_to_add = total_seats - target_available_seats
            
            
            passengers_to_add = min(passengers_to_add, len(available_passengers))
            
            
            if passengers_to_add > 0:
                selected_passengers = random.sample(available_passengers, passengers_to_add)
                for passenger in selected_passengers:
                    ride.passengers.add(passenger)
            
            rides.append(ride)
        
        return rides

    def create_chats(self, users, rides, count):
        """Crea chats de prueba."""
        chats = []
        
        for _ in range(count):
            ride = random.choice(rides)
            
            
            participant1 = ride.driver
            
            
            potential_participants = [u for u in users if u != participant1]
            if not potential_participants:
                continue
            participant2 = random.choice(potential_participants)
            
            
            if hasattr(ride, 'chat') and ride.chat is not None:
                continue
            
            
            chat = Chat.objects.create()
            chat.participants.add(participant1, participant2)
            
            
            
            Ride.objects.filter(id=ride.id).update(chat=chat)
            
            
            ride.refresh_from_db()
            
            chats.append(chat)
        
        return chats

    def create_messages(self, chats, count):
        """Crea mensajes de prueba en los chats."""
        messages = []
        for _ in range(count):
            chat = random.choice(chats)
            participants = list(chat.participants.all())
            sender = random.choice(participants)
            content = self.generate_random_text(5, 100)
            now = timezone.now()
            created_at = now - timedelta(days=random.randint(0, 30),
                                         hours=random.randint(0, 23),
                                         minutes=random.randint(0, 59))
            is_read = random.choice([True, False, True, True])
            msg = Message.objects.create(
                chat=chat,
                sender=sender,
                content=content,
                created_at=created_at,
                is_read=is_read
            )
            messages.append(msg)
        return messages

    def create_reports(self, users, rides, count):
        """Crea reportes de prueba."""
        reports = []
        
        report_types = ['user', 'ride', 'payment', 'system']
        importance_levels = ['normal', 'important', 'urgent']
        
        
        report_titles = [
            "Comportamiento inadecuado",
            "Conductor no apareció",
            "Viaje cancelado sin aviso",
            "Error en el pago",
            "Problema con la aplicación",
            "Usuario inapropiado",
            "Vehículo en mal estado",
            "No respeta las normas",
            "Cobro incorrecto",
            "Fallos técnicos en la web"
        ]
        
        for _ in range(count):
            
            reporter = random.choice(users)
            
            
            report_type = random.choice(report_types)
            
            
            reported_ride = None
            reported_payment = None
            
            if report_type == 'ride':
                reported_ride = random.choice(rides)
                
            
            title = random.choice(report_titles)
            description = self.generate_random_text(20, 200)
            
            
            importance = random.choice(importance_levels)
            
            
            created_at = timezone.now() - timedelta(days=random.randint(0, 30))
            
            
            read = random.choice([True, False])
            
            
            report = Report.objects.create(
                title=title,
                description=description,
                report_type=report_type,
                importance=importance,
                user=reporter,
                ride=reported_ride,
                payment=reported_payment,
                created_at=created_at,
                read=read
            )
            
            
            if random.random() < 0.6:  
                
                admin = random.choice([u for u in users if u.is_staff]) if any(u.is_staff for u in users) else reporter
                report.response = self.generate_random_text(20, 150)
                report.response_by = admin
                report.response_at = created_at + timedelta(days=random.randint(1, 5))
                report.read = True
                report.save()
            
            reports.append(report)
        
        return reports

    def create_payments(self, users, rides, count):
        """Crea pagos de prueba."""
        payments = []
        
        status_choices = ['PENDING', 'COMPLETED', 'FAILED', 'REFUNDED', 'CANCELLED']
        status_weights = [0.2, 0.6, 0.1, 0.05, 0.05]  
        
        
        payment_methods = ['CREDIT_CARD', 'BANK_TRANSFER', 'PAYPAL', 'STRIPE']
        
        for _ in range(count):
            
            ride = random.choice(rides)
            
            
            potential_payers = [u for u in users if u != ride.driver]
            if not potential_payers:
                continue
            payer = random.choice(potential_payers)
            
            
            recipient = ride.driver
            
            
            amount = Decimal(str(round(float(ride.price) * random.uniform(0.8, 1.0), 2)))
            
            
            status = random.choices(status_choices, weights=status_weights)[0]
            
            
            created_at = timezone.now() - timedelta(days=random.randint(0, 60))
            
            
            concept = f"Pago de viaje: {ride.origin} → {ride.destination}"
            
            
            stripe_id = None
            if status in ['COMPLETED', 'REFUNDED']:
                stripe_id = 'pi_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
            
            
            refund_id = None
            if status == 'REFUNDED':
                refund_id = 're_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
            
            payment = Payment.objects.create(
                payer=payer,
                recipient=recipient,
                ride=ride,
                amount=amount,
                status=status,
                created_at=created_at,
                concept=concept,
                payment_method=random.choice(payment_methods),
                stripe_payment_intent_id=stripe_id,
                stripe_refund_id=refund_id
            )
            
            payments.append(payment)
        
        return payments

    def generate_random_text(self, min_words, max_words):
        """Genera texto aleatorio con sentido."""
        words = [
            "viaje", "coche", "conductor", "pasajero", "carretera", "ruta", "compartir", 
            "ciudad", "destino", "origen", "hora", "salida", "llegada", "precio", "asiento", 
            "reserva", "mensaje", "chat", "usuario", "perfil", "pago", "reembolso", "cancelación",
            "problema", "solución", "ayuda", "contacto", "experiencia", "opinión", "valoración",
            "bueno", "malo", "excelente", "terrible", "agradable", "incómodo", "puntual", "tarde",
            "rápido", "lento", "amable", "descortés", "atento", "educado", "profesional", "principiante",
            "mucho", "poco", "algo", "nada", "todo", "algunos", "varios", "pocos", "muchos",
            "gracias", "por favor", "disculpa", "perdón", "hola", "adiós", "hasta pronto", "nos vemos"
        ]
        
        connecting_words = ["y", "o", "pero", "porque", "si", "cuando", "aunque", "además", "también", "sin embargo"]
        
        sentence_starters = [
            "Quisiera", "Me gustaría", "Necesito", "Debo", "Voy a", "Tengo que",
            "Puedo", "No puedo", "He decidido", "Estoy", "No estoy", "Podemos",
            "El", "La", "Los", "Las", "Un", "Una", "Unos", "Unas", "Este", "Esta",
            "Mi", "Tu", "Su", "Nuestro", "Vuestro"
        ]
        
        sentence_enders = [".", ".", ".", "!", "?"]
        
        
        num_words = random.randint(min_words, max_words)
        text = []
        current_sentence = []
        
        while sum(1 for _ in text) + sum(1 for _ in current_sentence) < num_words:
            
            if not current_sentence:
                current_sentence.append(random.choice(sentence_starters))
            
            
            words_in_sentence = random.randint(3, 8)
            for _ in range(words_in_sentence):
                if sum(1 for _ in text) + sum(1 for _ in current_sentence) >= num_words:
                    break
                
                if random.random() < 0.2 and current_sentence:  
                    current_sentence.append(random.choice(connecting_words))
                else:
                    current_sentence.append(random.choice(words))
            
            
            current_sentence.append(random.choice(sentence_enders))
            text.append(" ".join(current_sentence))
            current_sentence = []
        
        return " ".join(text)
