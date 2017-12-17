from django.shortcuts import redirect

from hello.models import Event

def current(request):
    current_events = Event.objects.filter(is_current=True).order_by('pk')
    if len(current_events):
        return redirect('/events/%d/join' % current_events[0].id)

    return redirect('/')