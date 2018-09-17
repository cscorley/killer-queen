import itertools
import logging
import random
import statistics

logger = logging.getLogger('hello')

from django.contrib.auth.models import (User, Group)
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import trueskill

from hello.models import *
from hello.trueskill_environment import skill_env

from redis.exceptions import ConnectionError
from rq import Queue
from worker import conn

q = Queue(connection=conn)


def refresh_ratings(request):
    try:
        result = q.enqueue(refresh_ratings_internal)
    except ConnectionError:
        refresh_ratings_internal()

    return HttpResponse('OK')

def refresh_ratings_internal():
    """
    Reset and re-rank all players based on all game results
    """

    # reset all players back to default rating
    for player in Player.objects.all(): # type: Player
        player.clear_stats()

    result: GameResult
    for result in GameResult.objects.order_by('created'):
        result.process()


class TeamViewItem:

    def __init__(self, name, players):
        self.name = name
        self.players = players
        self.rating_mean = 0.0
        self.rating_median = 0.0
        self._sort()

    def _sort(self):
        self.players = list(sorted(self.players, key=lambda player: player.user.id if player else 9999))

        if self.players:
            self.rating_mean = statistics.mean([x.trueskill_rating_exposure if x else 0 for x in self.players])
            self.rating_median = statistics.median([x.trueskill_rating_exposure if x else 0 for x in self.players])


    def add_player(self, player: Player) -> None:
        self.players.append(player)
        self._sort()


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

def team_suggestions_internal(event: Event, max_players_per_team: int, min_teams: int,
                              player_sorting_key=None, queen_sorting_key=None):
    player: Player
    players: List[Player] = list(event.players.all())

    players = list(filter(lambda player: player.user.is_active == True, players))

    if len(players) == 0:
        return list()
    elif len(players) == 1:
        return [TeamViewItem("Loneliest team", players)]

    # shuffle players so any equal ratings are out of order
    random.shuffle(players)

    team_ratio = len(players) / max_players_per_team
    if team_ratio % 1 > 0:
        team_ratio = int(team_ratio + 1)
    else:
        team_ratio = int(team_ratio)
    team_size: int = max(min_teams, team_ratio)

    logger.info("Team size: %d", team_size)
    logger.info("Players: %d", len(players))

    queens = [player for player in players if player.wants_queen]
    bees = [player for player in players if not player.wants_queen]

    # now sort by rating
    if player_sorting_key:
        logger.info("Sorting bees")
        bees = list(sorted(bees, key=player_sorting_key, reverse=True))

    if queen_sorting_key:
        logger.info("Sorting queens")
        queens = list(sorted(queens, key=queen_sorting_key, reverse=True))

    logger.info("Queens: %d, %s", len(queens), queens)
    logger.info("Bees: %d, %s", len(bees), bees)

    players = queens + bees

    full_teams = []
    teams = []
    team_names = random.sample([r.name for r in RandomName.objects.all()], team_size)
    for name in team_names:
        teams.append(TeamViewItem(name, list()))

    current_team = 0
    for player in players:
        min_teams = _teams_with_least_players(teams)
        team = min(min_teams, key=lambda t: t.rating_mean)

        # move any full teams
        while len(team.players) >= max_players_per_team:
            full_teams.append(team)
            teams.remove(team)

            min_teams = _teams_with_least_players(teams)
            team = min(min_teams, key=lambda t: t.rating_mean)


        team.add_player(player)
        current_team = teams.index(team)

        logger.info("Team: %d, %.2f \t Player: %.2f", current_team, team.rating_mean, player.trueskill_rating_exposure)

    # re-add the Nones so they're displayed
    # seems bad, man
    for team in teams:
        while len(team.players) < max_players_per_team:
            team.add_player(None)

        full_teams.append(team)

    return sorted(full_teams, key=lambda team: team.rating_mean, reverse=True)


def _teams_with_least_players(teams):
    min_players = min(len(team.players) for team in teams)
    return [team for team in teams if len(team.players) == min_players]

