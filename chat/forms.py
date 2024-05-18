from django import forms

from .models import Profile, ChatRoom


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'chat_rooms', 'profile_picture']
        widgets = {'chat_rooms': forms.CheckboxSelectMultiple()}
        labels = {'chat_rooms': 'Chat Rooms'}

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['user'].required = False
        self.fields['user'].widget.attrs['id'] = 'user_field'
        self.fields['chat_rooms'].widget.attrs['id'] = 'chat_rooms_field'
        self.fields['profile_picture'].widget.attrs['id'] = 'profile_picture_field'




class ChatRoomForm(forms.ModelForm):
    class Meta:
        model=ChatRoom
        fields=['name','members']

    def __init__(self, *args, **kwargs):
        super(ChatRoomForm, self).__init__(*args, **kwargs)
        
        # Form alanlarına id özniteliği ekleme
        self.fields['name'].widget.attrs['id'] = 'name_field'
        self.fields['members'].widget.attrs['id'] = 'members_field'
