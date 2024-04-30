from django import forms
from .models import User, Profile



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['chat_rooms', 'profile_picture','user']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['chat_rooms'].widget.attrs['class'] = 'form-control'  # İsteğe bağlı: Sohbet odaları için CSS sınıfı ekleme

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)
        if commit:
            profile.save()
        return profile

def ChatRoomForm():

    class Meta:
        model=ChatRoomForm()
        fields=['chat_rooms' , 'members' , 'name']
