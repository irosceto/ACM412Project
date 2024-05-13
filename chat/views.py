
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.authtoken.serializers import AuthTokenSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED


from .forms import ProfileForm, ChatRoomForm
from .models import Profile, ChatRoom
from .serializers import ProfileSerializer, ChatRoomSerializer, TokenSerializer
from django.contrib.auth.models import User
from .serializers import UserSerializer


from rest_framework.decorators import api_view
from django.contrib.auth import authenticate

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST



class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=HTTP_200_OK)



@api_view(['POST'])
def register(request):
    if request.method == 'POST':

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'success': True, 'message': 'User registered successfully.'}, status=HTTP_201_CREATED)
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=HTTP_400_BAD_REQUEST)




#@api_view(['POST'])
#def user_login(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        # Kullanıcıyı doğrula
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=400)
    else:
       return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


@api_view(['POST'])
def user_logout(request):
    logout(request)  # Kullanıcıyı oturumdan çık

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

@api_view(['GET'])
def chat_room_list(request):
    chat_rooms = ChatRoom.objects.all()
    serializer = ChatRoomSerializer(chat_rooms, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat_room(request):
    if request.method == 'POST':
        form = ChatRoomForm(request.data)
        if form.is_valid():
            chat_room = form.save()
            chat_room.members.add(request.user)
            serializer = ChatRoomSerializer(chat_room)
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response({'success': False, 'errors': form.errors}, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_chat_room(request):
    search_query = request.data.get('search_query')
    chat_rooms = ChatRoom.objects.filter(name__icontains=search_query, members=request.user)
    serializer = ChatRoomSerializer(chat_rooms, many=True)
    return Response(serializer.data)
