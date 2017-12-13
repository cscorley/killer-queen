from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.  So we know what to call you.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. This will allow you to reset your password.')

    class Meta:
        model = User
        fields = ('username',
                 'first_name',
                 'last_name',
                 'email',
                 'password1',
                 'password2', )

class EventRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, help_text='Required.  If you forgot your name, please ask for help! :-)')
