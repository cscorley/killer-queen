import itertools
import logging
import random

logger = logging.getLogger('hello')

from django.contrib.auth.models import (User, Group)
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import trueskill

from hello.models import *
from hello.trueskill_environment import skill_env

def refresh_ratings(request):
    """
    Reset and re-rank all players based on all game results
    """

    # reset all players back to default rating
    for player in Player.objects.all(): # type: Player
        player.update_rating(skill_env.Rating())

    result: GameResult
    for result in GameResult.objects.order_by('created'):
        result.process()

    return HttpResponse('OK')


def team_suggestions(request):
    """
    Generates a set of suggested players for gameplay

    It will distribute top players across teams evenly.  If there are to be 4 teams,
    with players ranked 1..16:

    [(1, 8, 9, 16),
     (2, 7, 10, 15),
     (3, 6, 11, 14),
     (4, 5, 12, 13)]
    """

    event_id = int(request.GET['event_id'])

    max_players_per_team = 5
    if 'max_players_per_team' in request.GET:
        max_players_per_team = int(request.GET['max_players_per_team'])

    min_teams = 2
    if 'min_teams' in request.GET:
        min_teams = int(request.GET['min_teams'])

    teams = team_suggestions_internal(event_id, max_players_per_team, min_teams)

    return JsonResponse({num: [{'id': player.pk, 'name': player.user.username} for player in team] for num, team in enumerate(teams)})

def team_suggestions_internal(event: Event, max_players_per_team: int, min_teams: int, sorting_key=None):
    player: Player
    players: List[Player] = list(event.players.all())

    # shuffle players so any equal ratings are out of order
    random.shuffle(players)

    # now sort by rating
    if sorting_key:
        players = sorted(players, key=sorting_key, reverse=True)

    if len(players) == 0:
        return list()
    elif len(players) == 1:
        return [players]

    team_size: int = max(min_teams, int((len(players) / max_players_per_team) + 0.5))

    walk_on_count = len(players) % team_size
    if walk_on_count > 0:
        players += [None] * (team_size - walk_on_count)

    logger.info("Players: %d", len(players))

    # https://stackoverflow.com/a/10364399
    # group the players into a 2D matrix:
    # [(1, 2, 3, 4),
    #  (5, 6, 7, 8)]
    groups = list(zip(*[iter(players)]*team_size))

    while (len(groups) > max_players_per_team):
        team_size += 1
        groups = list(zip(*[iter(players)]*team_size))

    logger.info("Group size initial: %d", len(groups))
    logger.debug("Groups: %s", str(groups))

    # reverse the odd groups so they are ranked high to low
    # [(1, 2, 3, 4),
    #  (8, 7, 6, 5),
    for num, group in enumerate(groups):
        if (num % 2 == 1):
            groups[num] = list(reversed(group))
        elif (num == len(groups) - 1):
            # always flip the last group if it wasn't already flipped
            # this ensures the worst players (or walk-ons/empty slots) are paired with the best
            groups[-1] = list(reversed(groups[-1]))

    logger.info("Group size reverse: %d", len(groups))
    logger.debug("Groups: %s", str(groups))

    # https://stackoverflow.com/a/4937526
    # create teams by transposing the matrix
    # [(1, 8,
    #  (2, 7,
    #  (3, 6,
    #  (4, 5,
    groups = list(list(x) for x in zip(*groups))

    logger.info("Group size final: %d", len(groups))
    logger.debug("Groups: %s", str(groups))

    grouped_players = sum(groups, list())
    logger.info("Grouped players: %d", len(grouped_players))

    # remove the None players
    for num, group in enumerate(groups):
        groups[num] = [item for item in group if item]

    players_on_teams = [player for team in groups for player in team if player is not None]
    teamless_players = [player for player in players if player not in players_on_teams]

    while teamless_players:
        player = teamless_players.pop()
        if player:
            for team in reversed(groups):
                if len(team) < max_players_per_team:
                    team.append(player)
                    break

    # re-add the Nones so they're displayed
    # seems bad, man
    for team in groups:
        while len(team) < max_players_per_team:
            team.append(None)

    return groups
