from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import Room, User

# from django.contrib.auth.models import User

# MyUserCreationForm est le formulaire d'inscription
class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2']

# Formulaire de création des salles
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

# Formulaire de connexions
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('avatar','name','username','email','bio')
        required = ['name','username','email']
