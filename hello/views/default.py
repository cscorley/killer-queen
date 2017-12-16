from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from hello.api import team_suggestions_internal
from hello.forms import SignUpForm, EventRegistrationForm
from hello.models import Player, EventPlayer, Event
from hello.trueskill_environment import skill_env

import logging

logger = logging.getLogger('hello')

def index(request):
    return render(request, 'index.html')

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

def event_current(request):
    current_events = Event.objects.filter(is_current=True).order_by('pk')
    if len(current_events):
        return redirect('/events/%d/join' % current_events[0].id)

    return redirect('/')

def event_join(request, event_id):
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
            user = authenticate(username=user.username, password=raw_password)
            register_player(event, user.username)
        elif registerForm.is_valid():
            register_player(event, registerForm.cleaned_data.get('username'))

        signUpForm = SignUpForm()
        registerForm = EventRegistrationForm()

    teams = team_suggestions_internal(event, max_players_per_team, min_teams)
    logger.info("Got teams: %s", str(teams))

    return render(request, 'event-join.html', {'signUpForm': signUpForm,
                                               'registerForm': registerForm,
                                               'teams': teams,
                                               'event': event})

def register_player(event: Event, username: str):
    user = User.objects.get_by_natural_key(username)
    ep = EventPlayer()
    ep.event = event
    ep.player = user.player
    try:
        ep.validate_unique()
        ep.save()
    except ValidationError:
        pass
