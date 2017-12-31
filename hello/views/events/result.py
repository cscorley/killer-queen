from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from hello.models import Event, GameResult, EventTeam, TeamMembership
from hello.forms import CreateGameResultForm, CreateTeamForm
from hello.views import Alert
import logging

logger = logging.getLogger("hello")


def result(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)
    games = GameResult.objects.filter(event=event).order_by('created')

    data = {'event':event}
    # TODO: filter team options by those on the event
    resultForm = CreateGameResultForm(data)
    teamForm = CreateTeamForm()
    alert = None

    if request.method == 'POST':
        logger.info(str(request.POST))
        resultForm = CreateGameResultForm(request.POST)
        teamForm = CreateTeamForm(request.POST)

        if resultForm.is_valid():
            result = resultForm.save()
            result.save()

            try:
                eventTeam = EventTeam(event=event, team=result.blue)
                eventTeam.save()
            except ValidationError:
                pass

            try:
                eventTeam = EventTeam(event=event, team=result.gold)
                eventTeam.save()
            except ValidationError:
                pass

            alert = Alert("Created new result.", "success", 5000)
        elif teamForm.is_valid():
            team = teamForm.save()
            team.save()

            for player in teamForm.cleaned_data.get('players'):
                members = TeamMembership(team=team, player=player)
                members.save()

            eventTeam = EventTeam(event=event, team=team)
            eventTeam.save()

            alert = Alert("Created new team.", "success", 5000)
        else:
            alert = Alert("Both forms were invalid.", "danger", 10000)

        resultForm = CreateGameResultForm(data)
        teamForm = CreateTeamForm()

    return render(request, 'event-result.html', {'games': games,
                                                 'event': event,
                                                 'resultForm': resultForm,
                                                 'teamForm': teamForm,
                                                 'alert': alert})