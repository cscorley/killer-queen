from django.shortcuts import render
from hello.models import Event, GameResult, EventTeam, TeamMembership
from hello.forms import CreateGameResultForm, CreateTeamForm
from hello.views import Alert
import logging

logger = logging.getLogger("hello")


def kiosk(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)
    games = GameResult.objects.filter(event=event).order_by('created')

    return render(request, 'event-kiosk.html', {'games': games,
                                                'event': event })
