from django.shortcuts import redirect

from hello.models import Event

def current(request):
    current_events = Event.objects.filter(is_current=True).order_by('when', 'pk')
    if len(current_events):
        return redirect('/events/%d/join' % current_events[0].id)

    return redirect('/')

def current_kiosk(request):
    current_events = Event.objects.filter(is_current=True).order_by('when', 'pk')
    if len(current_events):
        return redirect('/events/%d/kiosk' % current_events[0].id)

    return redirect('/kiosk')
