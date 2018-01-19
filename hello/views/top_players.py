from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse

from hello.models import Player

import statistics
import logging

logger = logging.getLogger("hello")

def top_players(request):
    players = Player.objects.all()
    players = sorted(players, key=lambda player: player.trueskill_rating_exposure, reverse=True)

    queen = players[0]
    if request.user.is_staff:
        bees = players[1:]
    else:
        bees = [player for player in players if player.confidence() > 50][1:10]

    return render(request, 'top-players.html', {'queen': queen,
                                                'bees': bees,
                                                })