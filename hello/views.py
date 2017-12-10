from django.shortcuts import render
from django.http import HttpResponse

from .models import Player

import requests
import os
import trueskill

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
    rating = trueskill.Rating()
    player = Player()
    player.name = 'test player'
    player.trueskill_rating_mu = rating.mu
    player.trueskill_rating_sigma = rating.sigma
    player.save()

    players = Player.objects.all()

    return render(request, 'db.html', {'players': players})

