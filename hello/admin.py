from django.contrib import admin

import inspect
from .models import *

# Register your models here.

admin.site.register((Player, Team, TeamMembership, GameResult, Event, EventTeam))
