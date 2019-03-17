from django.contrib import admin

from .models import Player, Team, TeamMembership, GameResult, Event, EventTeam, EventPlayer, RandomName, Season, CabInformation

# Register your models here.

admin.site.register((Player, Team, TeamMembership, GameResult, Event, EventTeam, EventPlayer, RandomName, Season, CabInformation))
