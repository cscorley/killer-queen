from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .api import team_suggestions_internal
from .forms import SignUpForm, EventRegistrationForm
from .models import Player, EventPlayer, Event
from .trueskill_environment import skill_env

import logging

logger = logging.getLogger('hello')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

def event_join(request, event_id):
    event_id = int(event_id)
    max_players_per_team = 5
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
            user = authenticate(username=user.username, password=raw_password)
            register_player(event_id, user.username)
            registerForm = EventRegistrationForm()
        elif registerForm.is_valid():
            register_player(event_id, registerForm.cleaned_data.get('username'))
            signUpForm = SignUpForm()


    teams = team_suggestions_internal(event_id, max_players_per_team, min_teams)
    logger.info("Got teams: %s", str(teams))

    return render(request, 'event-join.html', {'signUpForm': signUpForm,
                                               'registerForm': registerForm,
                                               'teams': teams})

def register_player(event_id: int, username: str):
    user = User.objects.get_by_natural_key(username)
    ep = EventPlayer()
    ep.event = Event.objects.get(pk=event_id)
    ep.player = user.player
    try:
        ep.validate_unique()
        ep.save()
    except ValidationError:
        pass
