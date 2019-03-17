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
        bracket = CabInformation(name="bracket", json="{}")
        bracket.save()

    try:
        gold_on_left = CabInformation.objects.get(pk="goldonleft")
    except ObjectDoesNotExist:
        gold_on_left = CabInformation(name="goldonleft", json="false")
        gold_on_left.save()

    return render(request, 'event-kiosk.html',
        {'event': event,
         'bracket': {'updated': bracket.updated, 'json': json.loads(bracket.json)},
         'goldonleft': {'updated': gold_on_left.updated, 'json': json.loads(gold_on_left.json)}
        })

def old_kiosk(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)

    return render(request, 'event-old-kiosk.html', {'event': event })
