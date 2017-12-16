from django.views.generic import ListView
from hello.models import Event

class EventListView(ListView):
    model = Event
