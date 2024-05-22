# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_name}'

        # Kullanıcı oturum durumunu kontrol et
        if self.scope['user'].is_authenticated:
            # WebSocket bağlantısını kabul etme
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # Oturum açmamış kullanıcıya bağlantıyı reddetme
            await self.close(code=4001)
