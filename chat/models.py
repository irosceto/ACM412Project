from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    chat_rooms = models.ManyToManyField('ChatRoom', related_name='membership')

    @classmethod
    def create_user(cls, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = cls.normalize_email(email)
        user = cls(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='chat_room_members')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_add)(
            f"chat_{self.id}",
            "chat_group",
        )

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{self.chat_room.id}",
            {
                "type": "chat_message",
                "message": {
                    "sender": self.sender.username,
                    "content": self.content
                }
            }
        )
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    chat_rooms = models.ManyToManyField(ChatRoom, related_name='memberships')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username if self.user else "Unassociated Profile"

    async def save(self, *args, **kwargs):
        await super().save(*args, **kwargs)
        channel_layer = get_channel_layer()
        for chat_room in self.chat_rooms.all():
            async_to_sync(channel_layer.group_add)(
                f"chat_{chat_room.id}",
                self.user.username,
            )

    async def delete(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        for chat_room in self.chat_rooms.all():
            async_to_sync(channel_layer.group_discard)(
                f"chat_{chat_room.id}",
                self.user.username,
            )
        await super().delete(*args, **kwargs)