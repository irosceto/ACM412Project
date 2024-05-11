"""
URL configuration for chatapplication project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from chat import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from chat.views import register, user_login, user_logout, profile_edit, chat_room_list, create_chat_room, \
    search_chat_room

urlpatterns = [
    path('api/register/', register, name='api_register'),
    path('api/login/', user_login, name='api_login'),
    path('api/logout/', user_logout, name='api_logout'),
    path('api/profile_edit/', profile_edit, name='api_profile_edit'),
    path('api/chat_rooms/', chat_room_list, name='api_chat_room_list'),
    path('api/create_chat_room/', create_chat_room, name='api_create_chat_room'),
    path('api/search_chat_room/', search_chat_room, name='api_search_chat_room'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
