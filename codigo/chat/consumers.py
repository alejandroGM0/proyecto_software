# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from accounts.public import update_last_activity
from .models import Chat
from .constants import CHAT_GROUP_FORMAT, MESSAGE_TYPE_CHAT, MESSAGE_NO_PERMISSION, ERROR_PROCESSING_MESSAGE
from ._utils import can_access_chat, format_message_for_api, save_chat_message, format_message_for_websocket

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        if not await self.verify_permission():
            return
            
        self.room_group_name = CHAT_GROUP_FORMAT.format(self.chat_id)
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
            message_content = data.get('message', '')
            
            if not message_content.strip():
                return
            
            formatted_message = await self.save_message(message_content)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': MESSAGE_TYPE_CHAT,
                    'message': formatted_message
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f"{ERROR_PROCESSING_MESSAGE}: {str(e)}"
            }))

    async def chat_message(self, event):
        message = event['message']
        
        await self.send(text_data=json.dumps({
            'message': message
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
        return can_access_chat(self.user, self.chat_id)

    @database_sync_to_async
    def update_user_activity(self):
        update_last_activity(self.user)

    @database_sync_to_async
    def save_message(self, message_content):
        message = save_chat_message(self.user, self.chat_id, message_content)
        return format_message_for_api(message)