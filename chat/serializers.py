from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile, ChatRoom, Message
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()






class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password','first_name','last_name']  # İhtiyaca göre alanları düzenleyebilirsiniz
        extra_kwargs = {
            'password': {'write_only': True},  # Şifre alanı sadece yazma (POST) için kullanılacak
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)  # create_user metodu, şifreyi otomatik olarak hashleyecektir
        return user



class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Profile
        fields = ['username', 'email', 'profile_picture']
class ChatRoomSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)  # members alanı birçoktan çok ilişki olduğu için many=True kullanılır

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'members']


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields =  fields = ['id', 'sender', 'recipient', 'content', 'chat_room_id']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user', 'email', 'profile_image')
