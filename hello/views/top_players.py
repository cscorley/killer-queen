from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, reverse
from django.db.models import Sum

from hello.models import Player, Season, GameResult, Event

import statistics
import logging
from datetime import date

logger = logging.getLogger("hello")

def top_players(request):
    if not request.user.is_superuser:
        current = Season.objects.filter(when__lte=date.today()).order_by('when', 'pk')
        logger.info("redirecting to current season top page: %d", current.id)
        return redirect(reverse('seasonal_top_players', args=[current.id]))

    players = Player.objects.filter(user__is_active=True).distinct()

    rank_queen, rank_bees = _split_queen(request, players, lambda player: player.trueskill_rating_exposure)
    map_ratio_queen, map_ratio_bees = _split_queen(request, players, lambda player: player.map_wins / max(1, player.map_losses))
    map_wins_queen, map_wins_bees = _split_queen(request, players, lambda player: player.map_wins)

    return render(request, 'top-players.html', {'rank_queen': rank_queen,
                                                'rank_bees': rank_bees,
                                                'map_ratio_queen': map_ratio_queen,
                                                'map_ratio_bees': map_ratio_bees,
                                                'map_wins_queen': map_wins_queen,
                                                'map_wins_bees': map_wins_bees,
                                                'title': 'All time'
                                                })

def _split_queen(request, players, sorter):
    bees = sorted(players, key=sorter, reverse=True)
    bees = [bee for bee in bees if len(bee.event_set.all()) >= 3]

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
        map_counts = { 'blue_wins': 0, 'blue_losses': 0, 'gold_wins': 0, 'gold_losses': 0}
        for team in qs:
            for gold in team.gold_result.values().filter(contributes_to_season_score=True).distinct():
                win_order = gold['win_order'].upper()
                map_counts['gold_wins'] += win_order.count('G')
                map_counts['gold_losses'] += win_order.count('B')

            for blue in team.blue_result.values().filter(contributes_to_season_score=True).distinct():
                win_order = blue['win_order'].upper()
                map_counts['blue_wins'] += win_order.count('B')
                map_counts['blue_losses'] += win_order.count('G')

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
