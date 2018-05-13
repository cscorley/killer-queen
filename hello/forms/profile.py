from django import forms
from django.contrib.auth.models import User, Group

from hello.models import Player

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('wants_queen', )
