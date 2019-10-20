from django.shortcuts import redirect

from hello.models import Event
from datetime import date

def get_todays_event() -> Event:
    current_events = Event.objects.filter(when__date=date.today()).order_by('when', 'pk')

    if len(current_events):
        return current_events[0]

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
