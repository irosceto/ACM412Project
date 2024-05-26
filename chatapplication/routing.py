from django.urls import path
from chatapplication.consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/<str:chat_room_id>/', ChatConsumer.as_asgi()),
]
