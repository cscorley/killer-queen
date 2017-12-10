from django.contrib.auth.models import (User, Group)
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

import trueskill

from .models import *
from .serializers import *

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
        player.update_rating(trueskill.Rating())

    for result in GameResult.objects.all(): # type: GameResult
        blue = list(result.blue.members.all()) # type: List[Player]
        gold = list(result.gold.members.all()) # type: List[Player]

        blue_ratings = [x.get_rating() for x in blue] # type: List[trueskill.Rating]
        gold_ratings = [x.get_rating() for x in gold] # type: List[trueskill.Rating]

        for _ in range(0, result.blue_win_count):
            blue_ratings, gold_ratings = trueskill.rate([blue_ratings, gold_ratings], ranks=[0, 1])

        for _ in range(0, result.gold_win_count):
            blue_ratings, gold_ratings = trueskill.rate([blue_ratings, gold_ratings], ranks=[1, 0])

        for player, rating in zip(blue, blue_ratings):
            player.update_rating(rating)

        for player, rating in zip(gold, gold_ratings):
            player.update_rating(rating)

    return HttpResponse('OK')

def team_suggestions(request):
    pass
