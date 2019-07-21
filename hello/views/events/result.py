from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from hello.models import Event, GameResult, EventTeam, TeamMembership
from hello.forms import CreateGameResultForm, CreateTeamForm
from hello.views import Alert
import logging
import json

logger = logging.getLogger("hello")


def result(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)
    games = GameResult.objects.filter(event=event).order_by('created')

    resultForm = get_new_result_form(event)

    teamForm = CreateTeamForm()
    alert = None

    if request.method == 'POST':
        logger.info(str(request.POST))
        resultForm = CreateGameResultForm(request.POST)
        teamForm = CreateTeamForm(request.POST)

        if resultForm.is_valid():
            result = resultForm.save(commit=False)
            result.event = event
            result.save()

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

        resultForm = get_new_result_form(event)
        teamForm = CreateTeamForm()

    return render(request, 'event-result.html', {'games': games,
                                                 'event': event,
                                                 'resultForm': resultForm,
                                                 'teamForm': teamForm,
                                                 'alert': alert,
                                                 'bracket': json.loads(event.cab_bracket),
                                                 })

def get_new_result_form(event: Event):
    data = {'event':event, 'contributes_to_season_score': True}
    resultForm = CreateGameResultForm(data)
    resultForm.fields['blue'].queryset = event.teams.all().order_by('name')
    resultForm.fields['gold'].queryset = event.teams.all().order_by('name')
    return resultForm
