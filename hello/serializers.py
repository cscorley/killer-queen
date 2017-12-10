from django.contrib.auth.models import User, Group

from rest_framework import serializers
from .models import (Player, Team, TeamMembership, GameResult)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class TeamMembershipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TeamMembership
        fields = '__all__'

class GameResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GameResult
        fields = '__all__'