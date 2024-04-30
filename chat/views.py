from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

from chat.forms import ProfileForm, ChatRoomForm
from chat.models import Profile, ChatRoom


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Burada 'home', kullanıcı kaydolduktan sonra yönlendirilecekleri URL'nin adı olmalı
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Burada 'home', kullanıcı giriş yaptıktan sonra yönlendirilecekleri URL'nin adı olmalı
    else:
        form = AuthenticationForm()
    return render(request, 'login/login.html', {'form': form})

def user_logout(request):
    logout(request)
     #return redirect('home')  # Burada 'home', kullanıcı çıkış yaptıktan sonra yönlendirilecekleri URL'nin adı olmalı




@login_required              #Profil görüntülüyor yoksa oluşturuyoruz
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
   # return render(request, 'profile/edit.html', {'form': form})



def chat_room_list(request):                                   #CHAT ROOMSLARI LİSTELEME GÖSTERME

    chat_rooms = ChatRoom.objects.all()
   # return render(request, 'chat/room_list.html', {'chat_rooms': chat_rooms})



@login_required                                           #Chat Room varsa members ekle o an ki kullanıcıyı yoksa oluştur
def create_chat_room(request):
    if request.method == 'POST':
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            chat_room = form.save()
            chat_room.members.add(request.user)
            return redirect('chat_room_list')
    else:
        form = ChatRoomForm()
   # return render(request, 'chat/create_room.html', {'form': form})



def search_chat_room(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        chat_rooms = ChatRoom.objects.filter(name__icontains=search_query, members=request.user)
        return render(request, 'your_template.html', {'chat_rooms': chat_rooms})
    else:
        chat_rooms = ChatRoom.objects.filter(members=request.user)
        return render(request, 'your_template.html', {'chat_rooms': chat_rooms})
