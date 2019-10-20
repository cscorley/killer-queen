import logging
import json

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from hello.forms import CreateGameResultForm, CreateTeamForm
from hello.models import CabInformation, Event
from hello.views import Alert

logger = logging.getLogger("hello")


def kiosk(request):
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

    return render(request, 'general-kiosk.html',
        {
            'bracket': {'updated': bracket.updated, 'json': json.loads(bracket.json)},
            'goldonleft': {'updated': gold_on_left.updated, 'json': json.loads(gold_on_left.json)}
        })
