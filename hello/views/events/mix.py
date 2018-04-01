
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from hello.forms import MixerForm
from hello.api import team_suggestions_internal
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


    team_names = random.sample([r.name for r in RandomName.objects.all()], len(teams))
    team_items = [TeamViewItem(team_name, team) for team_name, team in zip(team_names, teams)]
    team_items = sorted(team_items, key=lambda team: team.rating_mean, reverse=True)

    return render(request, 'event-mix-teams.html', {'form': form,
                                                    'teams': team_items,
                                                    'event': event,
                                                    'alert': alert,
                                                    'all_players': all_players})



class TeamViewItem:

    def __init__(self, name, players):
        self.name = name
        self.players = list(sorted(players, key=lambda player: player.user.id if player else 9999))
        self.rating_mean = statistics.mean([x.trueskill_rating_exposure if x else 0 for x in players])
        self.rating_median = statistics.median([x.trueskill_rating_exposure if x else 0 for x in players])


def register_player(event: Event, user: User) -> Alert:
    if user and event:
        logger.info("Registering user: %s", str(user))
        ep = EventPlayer()
        ep.event = event
        ep.player = user.player
        try:
            ep.validate_unique()
            ep.save()
            return Alert("Registered user: <strong>%s</strong>" % str(user), "success", 10000)
        except ValidationError:
            return Alert("Unable to register user: <strong>%s</strong>.  Is this user already registered?" % str(user), "warning", 15000)

    return Alert("Unable to register user.", "danger", 30000)

def unregister_player(event: Event, user: User) -> Alert:
    if user and event:
        logger.info("Removing user: <strong>%s</strong>", str(user))

        EventPlayer.objects.filter(event=event).filter(player=user.player).delete()
        return Alert("Removed user: <strong>%s</strong>" % str(user), "success", 10000)

    return Alert("Unable to remove user.", "danger", 30000)
