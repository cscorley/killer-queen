from django.contrib.auth import authenticate
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from hello.forms import SignUpForm, EventRegistrationForm
from hello.api import team_suggestions_internal
from hello.models import EventPlayer, Event

import statistics
import logging

logger = logging.getLogger("hello")

def join(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)
    max_players_per_team = 5  # TODO
    min_teams = 2
    signUpForm = SignUpForm()
    registerForm = EventRegistrationForm()

    if request.method == 'POST':
        signUpForm = SignUpForm(request.POST)
        registerForm = EventRegistrationForm(request.POST)

        if signUpForm.is_valid():
            user = signUpForm.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            register_player(event, user.username)
        elif registerForm.is_valid():
            register_player(event, registerForm.cleaned_data.get('username'))

        signUpForm = SignUpForm()
        registerForm = EventRegistrationForm()

    teams = team_suggestions_internal(event, max_players_per_team, min_teams)
    logger.info("Got teams: %s", str(teams))

    for team_num, team in enumerate(teams):
        logger.info("Team %d average: %f", team_num, statistics.mean([x.trueskill_rating_exposure if x else 0 for x in team]))

    return render(request, 'event-join.html', {'signUpForm': signUpForm,
                                               'registerForm': registerForm,
                                               'teams': teams,
                                               'event': event})

def register_player(event: Event, username: str):
    if username:
        user = User.objects.get(username__iexact=username) # retrieves a user by case insensitive username
        ep = EventPlayer()
        ep.event = event
        ep.player = user.player
        try:
            ep.validate_unique()
            ep.save()
        except ValidationError:
            pass