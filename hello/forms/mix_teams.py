
from dal import autocomplete
from django import forms

from hello.models import Player

class MixerForm(forms.Form):
    randomness = forms.IntegerField(initial=0, required=True, max_value=100, min_value=0)
    min_teams = forms.IntegerField(initial=2, required=True, max_value=100, min_value=0)
    max_players_per_team = forms.IntegerField(initial=5, required=True, max_value=5, min_value=0)

    def __init__(self, *args, **kwargs):
        super(MixerForm, self).__init__(*args, **kwargs)
