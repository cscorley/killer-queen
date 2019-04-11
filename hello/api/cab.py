

import json
import logging
from datetime import datetime

from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from hello.models import *

logger = logging.getLogger('hello')

@csrf_exempt
def bracket(request):
    processed =  _processCabInfo("bracket", request)

    if request.method == 'POST':
        try:
            current_events = Event.objects.filter(is_current=True).order_by('when', 'pk')
            if len(current_events):
                current_event = current_events[0]
                text = request.body.decode('utf-8')
                current_event.cab_bracket = text
                current_event.save()
        except:
            logger.error("you goofed while processing bracket text")

    return processed

@csrf_exempt
def goldonleft(request):
    return _processCabInfo("goldonleft", request)


def _processCabInfo(infoName, request):
    if request.method == 'POST':
        text = request.body.decode('utf-8')
        logger.debug(text)

        try:
            info = CabInformation.objects.get(pk=infoName)
            info.json = text
        except ObjectDoesNotExist:
            info = CabInformation(name=infoName, json=text)

        info.save()

        return JsonResponse({"updated": info.updated, "json": json.loads(info.json)})
    elif request.method == 'GET':
        try:
            info = CabInformation.objects.get(pk=infoName)
            return JsonResponse({"updated": info.updated, "json": json.loads(info.json)})
        except ObjectDoesNotExist:
            return HttpResponse()
