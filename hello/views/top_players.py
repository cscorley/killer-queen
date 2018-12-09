from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse
from django.db.models import Sum

from hello.models import Player, Season, GameResult

import statistics
import logging

logger = logging.getLogger("hello")

def top_players(request):
    players = Player.objects.filter(user__is_active=True).distinct()

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
    bees = [bee for bee in bees if len(bee.team_set.all()) >= 3]

    queen = None
    if bees:
        queen = bees[0]
        if request.user.is_superuser:
            bees = bees[1:]
        else:
            bees = bees[1:10]

    return queen, bees


def seasonal_top_players(request, season_id):
    season_id = int(season_id)
    season = Season.objects.get(pk=season_id)

    # players on teams in results for events this season
    players = Player.objects.filter(user__is_active=True).filter(team__event__season=season).distinct()
    logger.debug(players.query)
    player_map_wins = list()

    for player in players:
        qs = player.team_set.filter(event__season=season)
        blue_counts = qs.filter(blue_result__contributes_to_season_score=True).aggregate(
            blue_wins=Sum('blue_result__blue_win_count', distinct=True),
            blue_losses=Sum('blue_result__gold_win_count', distinct=True),
        )

        gold_counts = qs.filter(gold_result__contributes_to_season_score=True).aggregate(
            gold_wins=Sum('gold_result__gold_win_count', distinct=True),
            gold_losses=Sum('gold_result__blue_win_count', distinct=True),
        )

        map_counts = blue_counts
        map_counts.update(gold_counts)

        logger.debug(qs.query)

        for key, value in map_counts.items():
            if value is None:
                map_counts[key] = 0

        map_counts['player'] = player
        map_counts['total_wins'] = map_counts['blue_wins'] + map_counts['gold_wins']
        map_counts['total_losses'] = map_counts['blue_losses'] + map_counts['gold_losses']

        if player.id == 34:
            logger.debug(map_counts)

        player_map_wins.append(map_counts)

    player_map_wins.sort(key=lambda p: p['total_wins'], reverse=True)

    player_map_wins = filter(lambda x: x['total_wins'] > 0, player_map_wins)

    return render(request, 'seasonal-top-players.html', {'map_wins_bees': player_map_wins,
                                                         'title': season.name
                                                         })
