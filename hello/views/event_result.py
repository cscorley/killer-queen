from django.shortcuts import render, redirect
from hello.models import Event, GameResult, EventTeam

def event_result(request, event_id):
    event_id = int(event_id)
    event = Event.objects.get(pk=event_id)
    games = GameResult.objects.filter(event=event).order_by('created')

    return render(request, 'event-result.html', {'games': games,
                                                 'event': event})