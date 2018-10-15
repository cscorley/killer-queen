import json
import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render, reverse

from hello.api import TeamViewItem, team_suggestions_internal
from hello.forms import MixerForm
from hello.models import Event, EventTeam, Player, Team, TeamMembership
from hello.views import Alert


logger = logging.getLogger("hello")

def start(request, event_id):
    if not request.user.is_staff:
        reason = "Not allowed event %d, user %d" % (event.id, request.user.id)
        logger.info(reason)
        return HttpResponseNotAllowed(reason=reason)

    event_id = int(event_id)
    event: Event = Event.objects.get(pk=event_id)

    logger.info("hi friend")
    logger.info(str(request.body))

    if event.teams.exists():
        reason = "Event %d already has teams, failing" % event.id
        logger.info(reason)
        return HttpResponseBadRequest(reason=reason)

    raw_teams = json.loads(request.body)
    logger.info(str(raw_teams))
    for raw_team in raw_teams:
        team = Team(name=raw_team["name"])
        team.save()

        for raw_player in raw_team["players"]:
            player_id = raw_player["id"]
            if player_id:
                player = Player.objects.get(pk=player_id)
                membership = TeamMembership(team=team, player=player)
                membership.save()

        eventTeam = EventTeam(event=event, team=team)
        eventTeam.save()

    return HttpResponse()
