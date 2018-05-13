from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from hello.forms import SignUpForm, EventRegistrationForm, TokenForm
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

    max_players_per_team = 5  # TODO
    min_teams = 2
    signUpForm = SignUpForm()
    registerForm = EventRegistrationForm()
    tokenForm = TokenForm()
    alert = None

    all_players: List[Player] = list(event.players.order_by('eventplayer__created'))

    if not event.is_active and not request.user.is_staff:
        logger.info("redirecting to result page: %d", event.id)
        return redirect(reverse('event_result', args=[event.id]))

    token = ''
    has_token = (request.session.get('token', token) == event.token)
    if not request.user.is_staff and not has_token:
        if request.method == 'POST':
            tokenForm = TokenForm(request.POST)

        if tokenForm.is_valid():
            token = tokenForm.cleaned_data.get('token')

            if token == event.token:
                has_token = True
                request.session['token'] = token

        if not has_token:
            return render(request, 'event-join.html',
            {
                'signUpForm': None,
                'registerForm': None,
                'event': event,
                'alert': alert,
                'all_players': all_players,
                'tokenForm': tokenForm
            })
    elif request.method == 'POST':
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
            if alert.level == 'success':
                signUpForm = SignUpForm()

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

        all_players: List[Player] = list(event.players.order_by('eventplayer__created'))

    return render(request, 'event-join.html', {'signUpForm': signUpForm,
                                               'registerForm': registerForm,
                                               'event': event,
                                               'alert': alert,
                                               'all_players': all_players})


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
