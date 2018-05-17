from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse

from hello.models import Player

import statistics
import logging

logger = logging.getLogger("hello")

def top_players(request):
    players = Player.objects.all()

    rank_queen, rank_bees = _split_queen(request, players, lambda player: player.trueskill_rating_exposure)
    match_wins_queen, match_wins_bees = _split_queen(request, players, lambda player: player.match_wins)
    map_wins_queen, map_wins_bees = _split_queen(request, players, lambda player: player.map_wins)

    return render(request, 'top-players.html', {'rank_queen': rank_queen,
                                                'rank_bees': rank_bees,
                                                'match_wins_queen': match_wins_queen,
                                                'match_wins_bees': match_wins_bees,
                                                'map_wins_queen': map_wins_queen,
                                                'map_wins_bees': map_wins_bees,
                                                })

def _split_queen(request, players, sorter):
    bees = sorted(players, key=sorter, reverse=True)

    queen = bees[0]
    if request.user.is_superuser:
        bees = bees[1:]
    else:
        bees = [bee for bee in bees if len(bee.team_set.all()) >= 3][1:10]

    return queen, bees
