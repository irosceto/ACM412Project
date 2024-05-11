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



class ChatRoomForm(forms.ModelForm):

    class Meta:
        model=ChatRoom
        fields=[ 'members' , 'name']
