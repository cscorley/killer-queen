from django.shortcuts import redirect

from hello.models import Event
from datetime import date

def get_todays_event() -> Event:
    current_events = Event.objects.filter(is_current=True).order_by('when', 'pk')

    for event in current_events:
        if event.when.date == date.today():
            return event

    return None


def current(request):
    current_event = get_todays_event()
    if current_event:
        return redirect('/events/%d/join' % current_event.id)

    return redirect('/')

def current_kiosk(request):
    current_event = get_todays_event()
    if current_event:
        return redirect('/events/%d/kiosk' % current_event.id)

    return redirect('/kiosk')
