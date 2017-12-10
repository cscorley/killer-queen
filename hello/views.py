from django.shortcuts import render
from django.http import HttpResponse

from .models import Player

import requests
import os

# Create your views here.
# def index(request):
#     # return HttpResponse('Hello from Python!')
#     return render(request, 'index.html')

def index(request):
    times = int(os.environ.get('TIMES',3))
    return HttpResponse('Hello! ' * times)

    # r = requests.get('http://httpbin.org/status/418')
    # print(r.text)
    # return HttpResponse('<pre>' + r.text + '</pre>')

def db(request):
    player = Player()
    player.name = 'test player'
    player.save()

    players = Player.objects.all()

    return render(request, 'db.html', {'players': players})

