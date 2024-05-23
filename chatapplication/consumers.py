from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chat.models import Message, ChatRoom
from django.contrib.auth import get_user_model


import json
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_room_id = self.scope['url_route']['kwargs']['chat_room_id']
        self.room_group_name = f'chat_{self.chat_room_id}'

        # Set sender_id using user id from scope (assuming user is authenticated)
        self.sender_id = self.scope['user'].id

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save message to database and broadcast to room group
        await self.save_and_broadcast_message(message)

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id
        }))

    @database_sync_to_async
    def save_and_broadcast_message(self, message):
        room = ChatRoom.objects.get(id=self.chat_room_id)
        sender = User.objects.get(id=self.sender_id)
        Message.objects.create(chat_room=room, sender=sender, content=message)

        # Send message to room group
        self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender_id': self.sender_id,
                'message': message
            }
        )
