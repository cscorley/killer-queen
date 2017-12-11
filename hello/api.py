import itertools
import logging

logger = logging.getLogger('hello')

from django.contrib.auth.models import (User, Group)
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
import trueskill

from .models import *
from .serializers import *
from .trueskill_environment import skill_env

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class TeamMembershipViewSet(viewsets.ModelViewSet):
    queryset = TeamMembership.objects.all()
    serializer_class = TeamMembershipSerializer

class GameResultViewSet(viewsets.ModelViewSet):
    queryset = GameResult.objects.all()
    serializer_class = GameResultSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventTeamViewSet(viewsets.ModelViewSet):
    queryset = EventTeam.objects.all()
    serializer_class = EventTeamSerializer

class EventPlayerViewSet(viewsets.ModelViewSet):
    queryset = EventPlayer.objects.all()
    serializer_class = EventPlayerSerializer

def refresh_ratings(request):
    """
    Reset and re-rank all players based on all game results
    """

    # reset all players back to default rating
    for player in Player.objects.all(): # type: Player
        player.update_rating(skill_env.Rating())

    result: GameResult
    for result in GameResult.objects.all():
        blue: List[Player] = list(result.blue.members.all())
        gold: List[Player] = list(result.gold.members.all())

        blue_ratings: List[trueskill.Rating] = [x.get_rating() for x in blue]
        gold_ratings: List[trueskill.Rating] = [x.get_rating() for x in gold]

        for _ in range(0, result.blue_win_count):
            blue_ratings, gold_ratings = skill_env.rate([blue_ratings, gold_ratings], ranks=[0, 1])

        for _ in range(0, result.gold_win_count):
            blue_ratings, gold_ratings = skill_env.rate([blue_ratings, gold_ratings], ranks=[1, 0])

        for player, rating in zip(blue, blue_ratings):
            player.update_rating(rating)

        for player, rating in zip(gold, gold_ratings):
            player.update_rating(rating)

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

    event: Event = Event.objects.get(pk=event_id)
    player: Player
    players: List[Player] = sorted(event.players.all(),
                                   key=lambda player: player.trueskill_rating_exposure)

    team_count: int = max(min_teams, int(len(players) / max_players_per_team))

    logger.info("Teams: %d", team_count)

    # https://stackoverflow.com/a/10364399
    # group the players into a 2D matrix:
    # [(1, 2, 3, 4),
    #  (5, 6, 7, 8),
    #  (9, 10, 11, 12),
    #  (13, 14, 15, 16)]
    groups = list(zip(*[iter(players)]*team_count))

    # reverse the even groups so they are ranked high to low
    # [(1, 2, 3, 4),
    #  (8, 7, 6, 5),
    #  (9, 10, 11, 12),
    #  (16, 15, 14, 13)]
    for num, group in enumerate(groups):
        if (num % 2 == 1):
            groups[num] = list(reversed(group))

    # https://stackoverflow.com/a/4937526
    # create teams by transposing the matrix
    # [(1, 8, 9, 16),
    #  (2, 7, 10, 15),
    #  (3, 6, 11, 14),
    #  (4, 5, 12, 13)]
    teams = zip(*groups)

    return JsonResponse({num: [player.pk for player in team] for num, team in enumerate(teams)})
