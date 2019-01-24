from django.shortcuts import render
from hello.models import Event, GameResult, EventTeam, TeamMembership
from hello.forms import CreateGameResultForm, CreateTeamForm
from hello.views import Alert
import logging

logger = logging.getLogger("hello")


def kiosk(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)

    return render(request, 'event-kiosk.html', { 'event': event })