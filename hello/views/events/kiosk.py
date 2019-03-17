import logging
import json

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from hello.forms import CreateGameResultForm, CreateTeamForm
from hello.models import CabInformation, Event
from hello.views import Alert

logger = logging.getLogger("hello")


def kiosk(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)
    try:
        bracket = CabInformation.objects.get(pk="bracket")
    except ObjectDoesNotExist:
        bracket = None

    return render(request, 'event-kiosk.html',
        {'event': event,
         'bracket': {'updated': bracket.updated, 'json': json.loads(bracket.json)}})

def old_kiosk(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)

    return render(request, 'event-old-kiosk.html', {'event': event })
