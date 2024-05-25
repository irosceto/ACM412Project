import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import ChatRoom, Message
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['chat_room_id']
        self.room_group_name = f'chat_{self.room_id}'

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

    @database_sync_to_async
    def get_user(self):
        if self.scope['user'].is_authenticated:
            return self.scope['user']
        else:
            return None

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = await self.get_user()

        if sender:
            # Save message to database
            await self.save_message(sender, message)

            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender.username
                }
            )
        else:
            # Handle anonymous user or error
            pass
    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))


@database_sync_to_async
def save_message(self, sender, message):
    try:
        room = ChatRoom.objects.get(id=self.name)
    except ChatRoom.DoesNotExist:
        # Odanın bulunamaması durumunda burada uygun bir işlem yapılabilir.
        # Örneğin, bir hata kaydı oluşturulabilir veya uygun bir mesaj kullanıcıya gönderilebilir.
        print(f"Chat room with id {self.chat_room_id} does not exist.")
        return None

    message_obj = Message.objects.create(chat_room=room, sender=sender, content=message)
    return message_obj