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

    teams: List[List[Player]] = [list() for _ in range(0, team_count)]
    current_team = 0
    for player in players:
        logger.info("Assigning player %d to team %d", player.pk, current_team)
        teams[current_team].append(player)

        if current_team < team_count - 1:
            current_team += 1
        else:
            current_team = 0

    return JsonResponse({num: [player.pk for player in team] for num, team in enumerate(teams)})
