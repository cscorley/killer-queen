from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse
from django.db.models import Sum

from hello.models import Player, Season, GameResult

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
                                                'title': 'All time'
                                                })

def _split_queen(request, players, sorter):
    bees = sorted(players, key=sorter, reverse=True)

    queen = bees[0]
    if request.user.is_superuser:
        bees = bees[1:]
    else:
        bees = [bee for bee in bees if len(bee.team_set.all()) >= 3][1:10]

    return queen, bees


def seasonal_top_players(request, season_id):
    season_id = int(season_id)
    season = Season.objects.get(pk=season_id)

    # players on teams in results for events this season
    players = Player.objects.filter(team__event__season__id=season_id).distinct()
    player_map_wins = list()

    for player in players:
        map_counts = player.team_set.all().aggregate(blue_wins=Sum('blue_result__blue_win_count'),
                                                     blue_losses=Sum('blue_result__gold_win_count'),
                                                     gold_wins=Sum('gold_result__gold_win_count'),
                                                     gold_losses=Sum('gold_result__blue_win_count'))

        for key, value in map_counts.items():
            if value is None:
                map_counts[key] = 0

        map_counts['player'] = player
        map_counts['total_wins'] = map_counts['blue_wins'] + map_counts['gold_wins']
        map_counts['total_losses'] = map_counts['blue_losses'] + map_counts['gold_losses']
        player_map_wins.append(map_counts)

    player_map_wins.sort(key=lambda p: p['total_wins'], reverse=True)

    return render(request, 'seasonal-top-players.html', {'map_wins_bees': player_map_wins,
                                                        'title': season.name
                                                        })
