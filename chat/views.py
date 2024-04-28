from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserForm

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Kullanıcı kaydı başarılı, giriş sayfasına yönlendir
    else:
        form = UserForm()
    return render(request, 'registration/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user_name']
            password = form.cleaned_data['user_password']
            email = form.cleaned_data['user_email']
            # Kullanıcıyı doğrula
            user = authenticate(username=username, password=password, email=email)
            if user is not None:
                # Kullanıcı doğrulandıysa, giriş yap
                login(request, user)
                return redirect('home')  # Başarılı girişten sonra yönlendirilecek sayfa
                # Kullanıcının tarayıcısına çerez ekle
                response = HttpResponse("Başarılı giriş!")
                response.set_cookie('username', username)
                return response
            else:
                return HttpResponse("Geçersiz kullanıcı adı veya parola!")
    else:
        form = UserForm()
    return render(request, 'login.html', {'form': form})
