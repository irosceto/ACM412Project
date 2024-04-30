from django import forms
#from .models import User
from django.contrib.auth import User
from .models import Profile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['user_name', 'user_password', 'user_email']

class ProfileForm(forms.ModelForm):
    user_name = forms.CharField(max_length=100, required=True)  # Kullanıcı adını el ile ekliyoruz

    class Meta:
        model = Profile
        fields = ['user_name', 'chat_rooms', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['chat_rooms'].widget.attrs['class'] = 'form-control'  # İsteğe bağlı: Sohbet odaları için CSS sınıfı ekleme

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)
        user_name = self.cleaned_data.get('user_name')
        profile.user.username = user_name  # Profil ile ilişkili kullanıcı adını güncelle
        if commit:
            profile.save()
            profile.user.save()  # Kullanıcıyı da kaydet
        return profile
