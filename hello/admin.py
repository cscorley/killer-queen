from django.contrib import admin

import inspect
from .models import (Player, Team, TeamMembership, GameResult)

# Register your models here.

admin.site.register((Player, Team, TeamMembership, GameResult))
