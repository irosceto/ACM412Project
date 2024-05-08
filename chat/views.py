from contextvars import Token

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from chat.forms import ProfileForm, ChatRoomForm
from chat.models import Profile, ChatRoom

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse

from chat.serializers import ProfileSerializer, ChatRoomSerializer


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'message': 'User registered successfully.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@api_view(['POST'])
def user_login(request):
    serializer = ObtainAuthToken().get_serializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

def user_logout(request):
    logout(request)
     #return redirect('home')  # Burada 'home', kullanıcı çıkış yaptıktan sonra yönlendirilecekleri URL'nin adı olmalı




@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return Response({'success': True, 'message': 'Profile updated successfully.'})
        else:
            return Response({'success': False, 'errors': form.errors}, status=400)
    else:
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


@api_view(['GET'])
def chat_room_list(request):                                   #CHAT ROOMSLARI LİSTELEME GÖSTERME

    chat_rooms = ChatRoom.objects.all()
    serializer=ChatRoomSerializer(chat_rooms, many=True)
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
            return Response(serializer.data, status=201)  # 201 Created response
        else:
            return Response(form.errors, status=400)  # 400



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_chat_room(request):
    search_query = request.data.get('search_query')
    chat_rooms = ChatRoom.objects.filter(name__icontains=search_query, members=request.user)
    serializer = ChatRoomSerializer(chat_rooms, many=True)
    return Response(serializer.data)