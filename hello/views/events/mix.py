
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from hello.forms import MixerForm
from hello.api import team_suggestions_internal, TeamViewItem
from hello.models import EventPlayer, Event, RandomName
from hello.views import Alert

import logging

logger = logging.getLogger("hello")

def mix(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)

    if not request.user.is_staff:
        logger.info("redirecting to result page: %d", event.id)
        return redirect(reverse('event_join', args=[event.id]))

    teams_already_formed = event.teams.exists()

    max_players_per_team = 5
    min_teams = 2
    randomness = 1
    queen_randomness = 100
    form = MixerForm()
    alert = None

    all_players: List[Player] = list(event.players.order_by('eventplayer__created'))
    all_players = list(filter(lambda player: player.user.is_active == True, all_players))

    if request.method == 'POST':
        logger.info(str(request.POST))
        form = MixerForm(request.POST)

    if form.is_valid():
        max_players_per_team = form.cleaned_data.get('max_players_per_team')
        min_teams = form.cleaned_data.get('min_teams')
        randomness = form.cleaned_data.get('randomness')
        queen_randomness = form.cleaned_data.get('queen_randomness')


    teams = team_suggestions_internal(event,
                                      max_players_per_team,
                                      min_teams,
                                      randomness,
                                      queen_randomness)

    fake_id = -1
    teams_data = list()
    team: TeamViewItem
    for team in teams:
        team_data = { "name": team.name, "players": list(), "rating_mean": int(team.rating_mean) }
        player: Player
        for player in team.players:
            if player:
                team_data["players"].append({
                    "id": player.user.id,
                    "name": player.user.get_full_name(),
                    "rating": int(player.trueskill_rating_exposure),
                    "role": "👑" if player.wants_queen else "",
                    "team": team.name
                    })
            else:
                team_data["players"].append({ "id": fake_id, "name": "", "rating": 0, "team": team.name })
                fake_id -= 1
        teams_data.append(team_data)

    return render(request, 'event-mix-teams.html', {'form': form,
                                                    'teams': teams,
                                                    'event': event,
                                                    'alert': alert,
                                                    'all_players': all_players,
                                                    'teams_data': teams_data,
                                                    'teams_already_formed': teams_already_formed})

