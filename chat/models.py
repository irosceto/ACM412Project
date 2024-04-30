from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    chat_rooms = models.ManyToManyField('ChatRoom', related_name='member')


class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='user_chat_rooms')

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.content}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chat_rooms = models.ManyToManyField(ChatRoom, related_name='memberships')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username
