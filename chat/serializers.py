from rest_framework import serializers
from .models import Profile, ChatRoom


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username', 'email', 'profile_picture']  # Serileştirmek istediğiniz alanları buraya ekleyin
class ChatRoomSerializer(serializers.ModelSerializer):

 class Meta:
     model = ChatRoom
     fields = '__all__'


