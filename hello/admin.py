from django.contrib import admin

from .models import Player, Team, TeamMembership, GameResult, Event, EventTeam, EventPlayer

# Register your models here.

admin.site.register((Player, Team, TeamMembership, GameResult, Event, EventTeam, EventPlayer))
