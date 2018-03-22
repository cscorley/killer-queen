from dal import autocomplete
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from hello.models import Player

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='So we know what to call you.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional, but an initial would be helpful.')
    email = forms.EmailField(max_length=254, required=False, help_text='Optional, this will allow you to reset your password.')


    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = "Think of something clever.  Only letters and numbers, no spaces."
        self.fields['password1'].help_text = "Your password must contain at least 8 characters."
        self.fields['username'].widget.attrs.pop("autofocus", None)
        del self.fields['password2']

    class Meta:
        model = User
        fields = ('username',
                 'first_name',
                 'last_name',
                 'email',
                 'password1',)

class EventRegistrationForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url='user-autocomplete'),
        label="Player"
    )

    action = forms.ChoiceField(
        choices=[('A', 'Add'),
                 ('R', 'Remove')],
        required=False
    )
