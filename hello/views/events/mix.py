
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from hello.forms import MixerForm
from hello.api import team_suggestions_internal, TeamViewItem
from hello.models import EventPlayer, Event, RandomName
from hello.views import Alert

import statistics
import logging
import random

logger = logging.getLogger("hello")

def mix(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)

    if not request.user.is_staff:
        logger.info("redirecting to result page: %d", event.id)
        return redirect(reverse('event_join', args=[event.id]))

    max_players_per_team = 5  # TODO
    min_teams = 2
    randomness = 0
    form = MixerForm()
    alert = None

    all_players: List[Player] = list(event.players.order_by('eventplayer__created'))
    all_players = list(filter(lambda player: player.user.is_active == True, all_players))
    max_rating = max([x.trueskill_rating_exposure if x else 0 for x in all_players])

    if request.method == 'POST':
        logger.info(str(request.POST))
        form = MixerForm(request.POST)

        if form.is_valid():
            max_players_per_team = form.cleaned_data.get('max_players_per_team')
            min_teams = form.cleaned_data.get('min_teams')
            randomness = form.cleaned_data.get('randomness')

    rating_factor = (max_rating / 100) * randomness
    if randomness:
        sorter = lambda player: int(player.trueskill_rating_exposure / (rating_factor if rating_factor else 1))
    else:
        sorter = lambda player: player.trueskill_rating_exposure

    teams = team_suggestions_internal(event,
                                      max_players_per_team,
                                      min_teams,
                                      sorter)


    team_items = sorted(teams, key=lambda team: team.rating_mean, reverse=True)

    return render(request, 'event-mix-teams.html', {'form': form,
                                                    'teams': team_items,
                                                    'event': event,
                                                    'alert': alert,
                                                    'all_players': all_players})
