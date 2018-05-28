from dal import autocomplete
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from hello.models import Event, GameResult, EventTeam, Player, Team

class CreateGameResultForm(forms.ModelForm):
    class Meta:
        model = GameResult
        fields = ('blue',
                  'gold',
                  'blue_win_count',
                  'gold_win_count',
                  'event',
                  'contributes_to_season_score')
