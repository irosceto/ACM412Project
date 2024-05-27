from django.contrib.auth.models import User
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import TokenSerializer, MessageSerializer
from rest_framework_simplejwt.tokens import AccessToken
from .forms import ProfileForm
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status, generics



from .models import Profile, ChatRoom, Message
from .serializers import ProfileSerializer, ChatRoomSerializer, TokenSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if not username or not password:
            return Response({"message": "Username and password are required"}, status=HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name,
                                        last_name=last_name)
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Kullanıcıyı doğrula
        user = authenticate(request, username=username, password=password)

        if user:
            # Kullanıcı varsa giriş yap
            login(request, user)

            # Yenileme tokeni oluştur
            refresh_token = RefreshToken.for_user(user)

            # Erişim tokeni oluştur
            access_token = AccessToken.for_user(user)

            # Response oluştur
            return Response({
                'message': 'Login successful',
                'refresh_token': str(refresh_token),
                'access_token': str(access_token),
            }, status=status.HTTP_200_OK)
        else:
            # Kullanıcı yoksa hata mesajı döndür
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class TokenValidationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        serializer = TokenSerializer(instance=request.auth)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profile_edit(request):
    if request.method == 'POST':
        profile, created = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Profile updated successfully.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=HTTP_400_BAD_REQUEST)
    else:
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_room_list(request):
    try:
        chat_rooms = ChatRoom.objects.all()
        serializer = ChatRoomSerializer(chat_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat_room(request):
    try:
        user_id = request.user.id
        name = request.data.get('name')
        chat_room = ChatRoom.objects.create(name=name)

        # Oluşturan kullanıcıyı odaya ekle
        chat_room.members.add(request.user)

        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])  
@permission_classes([IsAuthenticated]) 
def room_detail(request, room_id):
    try:
        room = ChatRoom.objects.get(id=room_id)
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ChatRoom.DoesNotExist:
        return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_chat_room(request, room_id):
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
        chat_room.members.add(request.user)
        return Response({"message": "Successfully joined the chat room"}, status=status.HTTP_200_OK)
    except ChatRoom.DoesNotExist:
        return Response({"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_chat_room(request):
    try:
        search_query = request.data.get('search_query')
        chat_rooms = ChatRoom.objects.filter(name__icontains=search_query, members=request.user)
        serializer = ChatRoomSerializer(chat_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
class ChatRoomUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_room_id = self.kwargs['chat_room_id']
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        return chat_room.members.all()
