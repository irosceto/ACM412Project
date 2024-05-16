
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.authtoken.serializers import AuthTokenSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import ProfileForm, ChatRoomForm
from .models import Profile, ChatRoom
from .serializers import ProfileSerializer, ChatRoomSerializer, TokenSerializer
from django.contrib.auth.models import User
from .serializers import UserSerializer

from django.shortcuts import redirect
from django.urls import reverse

from rest_framework.decorators import api_view
from django.contrib.auth import authenticate

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .forms import ChatRoomForm  # ChatRoomForm'u import ediyoruz
from .models import ChatRoom
from .serializers import ChatRoomSerializer


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .forms import ChatRoomForm  # ChatRoomForm'u import ediyoruz
from .models import ChatRoom
from .serializers import ChatRoomSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST


from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

# Django REST Framework ve JWT'yı içe aktarın
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from django.contrib.auth import authenticate, login

from .serializers import UserSerializer

class RegisterUser(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    from rest_framework.authtoken.models import Token
    from rest_framework.authentication import SessionAuthentication, BasicAuthentication
    from rest_framework.permissions import IsAuthenticated

    class UserLogin(APIView):
        def post(self, request):
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    class UserLogout(APIView):
        authentication_classes = [SessionAuthentication, BasicAuthentication]
        permission_classes = [IsAuthenticated]

        def post(self, request):
            logout(request)
            return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)

    #class TokenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Token oluştur
        refresh_token = RefreshToken.for_user(request.user)
        access_token = refresh_token.access_token

        # Tokenları bir JSON yanıtı olarak dön
        return Response({
            'refresh': str(refresh_token),
            'access': str(access_token),
        })


#class TokenValidationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Doğrulanan kullanıcı bilgisini dön
        return Response({
            'user_id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            # Diğer kullanıcı bilgileri...
        })


@login_required
@api_view(['GET', 'POST'])
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

@login_required
@api_view(['GET'])
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
        # Oturum açmış kullanıcının kimliğini al
        user_id = request.user.id

        # HTTP isteğinden gelen verileri al
        name = request.data.get('name')

        # ChatRoom modelini kullanarak yeni bir oda oluştur
        chat_room = ChatRoom.objects.create(name=name)

        # Oturum açmış kullanıcıyı chat odası üyelerine ekle
        chat_room.members.add(user_id)

        # ChatRoom modelini serialize et ve HTTP yanıtı olarak dön
        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def search_chat_room(request):
    try:
        search_query = request.data.get('search_query')
        chat_rooms = ChatRoom.objects.filter(name__icontains=search_query, members=request.user)
        serializer = ChatRoomSerializer(chat_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)