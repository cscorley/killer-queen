
from dal import autocomplete
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from hello.models import Event, GameResult, EventTeam, Player, Team

class CreateTeamForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(
        queryset=Player.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='user-autocomplete'),
    )

    class Meta:
        model = Team
        fields = ('name', )