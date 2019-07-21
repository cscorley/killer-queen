import itertools
import logging
import random
import statistics
from datetime import datetime, timezone, timedelta

logger = logging.getLogger('hello')

from django.contrib.auth.models import (User, Group)
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import trueskill

from hello.models import *
from hello.trueskill_environment import skill_env, default_sigma

from redis.exceptions import ConnectionError
from rq import Queue
from worker import conn

q = Queue(connection=conn)

def refresh_ratings(request):
    if not request.user.is_staff:
        return HttpResponse("You don't have access to this.")

    # we need this for the first time processing
    full_reset = False
    try:
        full_reset = bool(request.GET.get("full_reset", False))
    except ValueError:
        pass # Got bad value

    try:
        result = q.enqueue(refresh_ratings_internal, full_reset)
    except ConnectionError:
        refresh_ratings_internal()

    return HttpResponse('OK -- updating ranks')

def refresh_ratings_internal(full_reset: bool):
    """
    Reset and re-rank all players based on all game results
    """

    if full_reset:
        # reset all players back to default rating
        event: Event
        for event in Event.objects.all():
            event.has_been_processed = False
            event.save()

        player: Player
        for player in Player.objects.all():
            player.clear_stats()

    # player rank confidence should decay 5% if missing
    decay_rate = 1.05

    now = datetime.now(timezone.utc)
    events: List[Event] = Event.objects.filter(when__lte=now, has_been_processed=False).order_by('when')

    event: Event
    for event in events:
        results: List[GameResult] = GameResult.objects.filter(event=event).order_by('created')

        updated_players = set()
        for result in results:
            result.process()

            updated_players.update(result.blue.members.all())
            updated_players.update(result.gold.members.all())

        all_players = set(Player.objects.all())
        decay_players = all_players - updated_players

        logger.info("Decaying %d of %d players for Event %s", len(decay_players), len(all_players), str(event))
        player: Player
        for player in all_players:
            rating: trueskill.Rating = player.get_rating()
            sigma = rating.sigma * decay_rate
            if sigma > default_sigma:
                sigma = default_sigma

            new_rating = skill_env.create_rating(rating.mu, sigma)
            player.update_rating(new_rating, 0, 0)

        event.has_been_processed = True
        event.save()

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
                              randomness: int, queen_randomness: int):
    player: Player
    players: List[Player] = list(event.players.all())

    players = list(filter(lambda player: player.user.is_active == True, players))

    if len(players) == 0:
        return list()
    elif len(players) == 1:
        return [TeamViewItem("Loneliest team", players)]

    max_rating = max([x.trueskill_rating_exposure if x else 0 for x in players])

    player_sorter = _get_sorter(randomness, max_rating, lambda p: p.trueskill_rating_exposure)
    queen_sorter = _get_sorter(queen_randomness, max_rating, lambda p: p.trueskill_rating_exposure)
    team_sorter = _get_sorter(randomness, max_rating, lambda t: t.rating_mean)
    team_queen_sorter = _get_sorter(queen_randomness, max_rating, lambda t: t.rating_mean)

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
    logger.info("Sorting bees")
    bees = list(sorted(bees, key=player_sorter, reverse=True))

    logger.info("Sorting queens")
    queens = list(sorted(queens, key=queen_sorter, reverse=True))

    logger.info("Queens: %d, %s", len(queens), queens)
    logger.info("Bees: %d, %s", len(bees), bees)

    players = queens + bees

    full_teams = []
    teams = []
    team_names = random.sample([r.name for r in RandomName.objects.all()], team_size)
    for name in team_names:
        teams.append(TeamViewItem(name, list()))

    _add_players(queens, teams, max_players_per_team, team_queen_sorter)
    _add_players(bees, teams, max_players_per_team, team_sorter)

    # re-add the Nones so they're displayed
    # seems bad, man
    for team in teams:
        while len(team.players) < max_players_per_team:
            team.add_player(None)

        full_teams.append(team)

    return sorted(full_teams, key=lambda team: team.rating_mean, reverse=True)

def _add_players(players, teams, max_players_per_team, sorter):
    for player in players:
        min_teams = _teams_with_least_players(teams)
        team = min(min_teams, key=sorter)

        # move any full teams
        while len(team.players) >= max_players_per_team:
            full_teams.append(team)
            teams.remove(team)

            min_teams = _teams_with_least_players(teams)
            team = min(min_teams, key=sorter)


        team.add_player(player)

        logger.info("Assigned Team: %s, %.2f \t Player: %s, %.2f", team.name, team.rating_mean, str(player.user), player.trueskill_rating_exposure)



def _teams_with_least_players(teams):
    min_players = min(len(team.players) for team in teams)
    return [team for team in teams if len(team.players) == min_players]

def _get_sorter(randomness: int, max_rating: float, key):
    if randomness:
        # Ensure all players are the same when we want completely random
        if randomness == 100:
            return lambda player: 0

        rating_factor = (max_rating / 100) * randomness
        return lambda player: int(key(player) / (rating_factor if rating_factor else 1))
    else:
        # If we have no randomness, don't bother
        return lambda player: key(player)

