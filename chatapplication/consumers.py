from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from chat.models import Message, User, Profile


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join the chat room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Get profiles of other users in the chat room
        profiles = Profile.objects.exclude(user=self.scope['user'])
        other_users = [{'username': profile.user.username, 'id': profile.user.id} for profile in profiles]

        # Send other users' profiles to the client
        await self.send(text_data=json.dumps({
            'other_users': other_users
        }))

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the chat room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if 'message' in text_data_json:
            message_content = text_data_json['message']
            sender_id = self.scope['user'].id
            recipient_id = text_data_json.get('recipient_id', None)

            # Check if recipient_id is provided
            if recipient_id is None:
                print("Recipient ID is not provided in the message.")
                return

            # Get the recipient user
            try:
                recipient_user = await sync_to_async(User.objects.get)(id=recipient_id)
            except User.DoesNotExist:
                print(f"Recipient with ID '{recipient_id}' not found.")
                return

            # Save the message to the database
            await sync_to_async(Message.objects.create)(
                chat_room_id=self.room_id,
                sender_id=sender_id,
                recipient_id=recipient_user.id,
                content=message_content
            )

            # Send the message to the chat room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message_content,
                    'sender': self.scope['user'].username,
                    'recipient': recipient_user.username
                }
            )
        else:
            # Handle the case when the received message does not have the 'message' key
            print("Received message does not have the 'message' key.")
            await self.send(text_data=json.dumps({
                'error': 'Received message does not have the "message" key.'
            }))

    async def chat_message(self, event):
        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'recipient': event['recipient']
        }))
    async def chat_message(self, event):
        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'recipient': event['recipient']
        }))
