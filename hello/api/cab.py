

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
    if request.method == 'POST':
        text = request.body.decode('utf-8')
        logger.debug(text)

        try:
            bracket = CabInformation.objects.get(pk="bracket")
            bracket.json = text
        except ObjectDoesNotExist:
            bracket = CabInformation(name="bracket", json=text)

        bracket.save()

        return JsonResponse({"updated": bracket.updated, "bracket": json.loads(bracket.json)})
    elif request.method == 'GET':
        try:
            bracket = CabInformation.objects.get(pk="bracket")
            return JsonResponse({"updated": bracket.updated, "bracket": json.loads(bracket.json)})
        except ObjectDoesNotExist:
            return HttpResponse()
