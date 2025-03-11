import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Message
from rides.models import Ride

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ride_id = self.scope['url_route']['kwargs']['ride_id']
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        authorized = await self.check_user_permission()
        if not authorized:
            await self.close()
            return
            
        self.room_group_name = f'chat_{self.ride_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            
            authorized = await self.check_user_permission()
            if not authorized:
                await self.close()
                return

            await self.save_message(self.user, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.user.username,
                    'timestamp': timezone.now().strftime('%H:%M')
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': 'Error processing message'
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'content': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def check_user_permission(self):
        try:
            ride = Ride.objects.get(id=self.ride_id)
            return self.user == ride.driver or self.user in ride.passengers.all()
        except Ride.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, message):
        ride = Ride.objects.get(id=self.ride_id)
        Message.objects.create(
            ride=ride,
            sender=user,
            content=message
        )