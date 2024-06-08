import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

import json
from rest_framework_simplejwt.tokens import AccessToken
from chat.models import ChatRoom, Message

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Extract chat room id from URL parameters
            self.room_id = self.scope['url_route']['kwargs']['chat_room_id']
            self.room_group_name = f'chat_{self.room_id}'

            # Extract query parameters
            query_params = parse_qs(self.scope['query_string'].decode())

            # Get access_token from query parameters
            access_token = query_params.get('access_token', [''])[0]

            # Authenticate user
            user = await self.authenticate_user(access_token)
            if user:
                self.user = user
            else:
                logger.error("Failed to authenticate user")
                await self.close()
                return

            # Join chat room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            past_messages = await self.get_room_messages(self.room_id)
            await self.send_past_messages(past_messages)
            logger.info(f"WebSocket connection established for user {self.user.username} with past messages sent")
           
        except Exception as e:
            logger.error(f"Error establishing WebSocket connection: {e}")
            await self.close()

    async def authenticate_user(self, access_token):
        try:
            # Decode the access token and get the user
            token = AccessToken(access_token)
            user_id = token['user_id']
            user = await database_sync_to_async(User.objects.get)(id=user_id)
            return user
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    async def disconnect(self, close_code):
        # Leave chat room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        if hasattr(self, 'user'):
            logger.info(f"WebSocket connection closed for user {self.user.username}")
        else:
            logger.info("WebSocket connection closed")

    async def receive(self, text_data):
        # Parse incoming JSON message
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            # Save the message to the database
            await self.save_message(self.user, self.room_id, message)
        except Exception as e:
            logger.error(f"Error parsing incoming message: {e}")
            return

        # Broadcast message to chat room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username if hasattr(self, 'user') else None
            }
        )

    @database_sync_to_async
    def save_message(self, user, room_id, message):
        try:
            room = ChatRoom.objects.get(id=room_id)
            Message.objects.create(sender=user, chat_room=room, content=message)
        except ChatRoom.DoesNotExist:
            logger.error(f"Chat room {room_id} does not exist")

    async def chat_message(self, event):
        # Send message to WebSocket
        try:
           await self.send(text_data=json.dumps({
            
              'content': event['message'],
              'sender': event.get('username', 'Anonymous')        
           })) 
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")

    @database_sync_to_async
    def get_room_messages(self, room_id):
        room = ChatRoom.objects.get(id=self.room_id)
        messages = room.messages.order_by('timestamp')[:50]  # Son 50 mesajı al
        return [{
            'id': message.id,
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for message in messages]
    
    async def send_past_messages(self, messages):
        for message in messages:
            await self.send(text_data=json.dumps({
                'type': 'old_message',
                'content': message['content'],
                'sender': message['sender'],
                'timestamp': message['timestamp']
            }))
    
