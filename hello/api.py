from tastypie.resources import ModelResource
from tastypie.api import Api
from .models import (Player, Team, TeamMembership, GameResult)

v1 = Api(api_name='v1')
class PlayerResource(ModelResource):
    class Meta:
        queryset = Player.objects.all()
v1.register(PlayerResource())

class TeamResource(ModelResource):
    class Meta:
        queryset = Team.objects.all()
v1.register(TeamResource())

class TeamMembershipResource(ModelResource):
    class Meta:
        queryset = TeamMembership.objects.all()
v1.register(TeamMembershipResource())

class GameResultResource(ModelResource):
    class Meta:
        queryset = GameResult.objects.all()
v1.register(GameResultResource())
