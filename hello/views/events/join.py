from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from hello.forms import SignUpForm, EventRegistrationForm
from hello.api import team_suggestions_internal
from hello.models import EventPlayer, Event, RandomName
from hello.views import Alert

import statistics
import logging
import random

logger = logging.getLogger("hello")

def join(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)

    if not event.is_active and not request.user.is_staff:
        logger.info("redirecting to result page: %d", event.id)
        return redirect(reverse('event_result', args=[event.id]))

    max_players_per_team = 5  # TODO
    min_teams = 2
    signUpForm = SignUpForm()
    registerForm = EventRegistrationForm()
    alert = None

    if request.method == 'POST':
        signUpForm = SignUpForm(request.POST)
        registerForm = EventRegistrationForm(request.POST)
        logger.info(str(request.POST))

        if signUpForm.is_valid():
            user = signUpForm.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = signUpForm.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            alert = register_player(event, user)
        elif registerForm.is_valid():
            user = registerForm.cleaned_data.get('user')
            action = registerForm.cleaned_data.get('action')

            if action == 'A':
                alert = register_player(event, user)
            elif action == 'R':
                alert = unregister_player(event, user)
            else:
                alert = register_player(event, user)

        signUpForm = SignUpForm()
        registerForm = EventRegistrationForm()

    teams = team_suggestions_internal(event,
                                      max_players_per_team,
                                      min_teams,
                                      lambda player: int(player.trueskill_rating_exposure))

    team_names = random.sample([r.name for r in RandomName.objects.all()], len(teams))
    team_items = [TeamViewItem(team_name, team) for team_name, team in zip(team_names, teams)]

    all_players: List[Player] = list(event.players.order_by('eventplayer__created'))

    return render(request, 'event-join.html', {'signUpForm': signUpForm,
                                               'registerForm': registerForm,
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