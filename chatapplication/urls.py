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

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


from chat.views import (
    RegisterUser,

    TokenValidationAPIView,
    profile_edit,
    chat_room_list,
    create_chat_room,
    search_chat_room,
    UserLogin,
    room_detail,
    RoomMembersView,
    profile_detail
)

from django.urls import path
from chat.views import (
    RegisterUser,  TokenValidationAPIView, profile_edit,
    chat_room_list, create_chat_room, join_chat_room, search_chat_room,UserLogin
)


urlpatterns = [
    path('api/register/', RegisterUser.as_view(), name='register'),
    path('api/login/', UserLogin.as_view(),name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),



    path('api/token/validate/', TokenValidationAPIView.as_view(), name='token_validation'),
    path('api/profile/', profile_edit, name='profile_edit'),
    path('api/chat_rooms/', chat_room_list, name='chat_room_list'),
    path('api/chat_rooms/create/', create_chat_room, name='create_chat_room'),
    path('api/chat_rooms/<int:room_id>/join/', join_chat_room, name='join_chat_room'),
    path('api/search_chat_room/', search_chat_room, name='search_chat_room'),
    path('api/chat_rooms/<int:room_id>', room_detail, name='room_detail'),
    path('chat_rooms/<int:chat_room_id>', RoomMembersView.as_view(), name='chat_room_users'),
    path('api/profile/<str:username>/', profile_detail, name='profile_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
