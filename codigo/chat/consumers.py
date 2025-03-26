import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Message
from rides.models import Ride
from accounts.public import update_last_activity
from .constants import (
    MESSAGE_NO_PERMISSION, 
    ERROR_PROCESSING_MESSAGE,
    CHAT_GROUP_FORMAT,
    MESSAGE_TYPE_CHAT
)
from ._utils import can_access_chat, save_chat_message, format_message_for_websocket

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ride_id = self.scope['url_route']['kwargs']['ride_id']
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        if not await self.verify_permission():
            return
            
        self.room_group_name = CHAT_GROUP_FORMAT.format(self.ride_id)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.update_user_activity()
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
            
            if not await self.verify_permission():
                return

            await self.save_message(message)
            message_data = format_message_for_websocket(message, self.user)
            await self.channel_layer.group_send(
                self.room_group_name,
                message_data
            )
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': ERROR_PROCESSING_MESSAGE
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'content': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))
        
    async def verify_permission(self):
        """Verifica si el usuario tiene permiso y cierra la conexión si no"""
        authorized = await self.check_user_permission()
        if not authorized:
            await self.send(text_data=json.dumps({'error': MESSAGE_NO_PERMISSION}))
            await self.close()
            return False
        return True

    @database_sync_to_async
    def check_user_permission(self):
        return can_access_chat(self.user, self.ride_id)

    @database_sync_to_async
    def update_user_activity(self):
        update_last_activity(self.user)

    @database_sync_to_async
    def save_message(self, message_content):
        save_chat_message(self.user, self.ride_id, message_content)