from django.views.generic import ListView
from hello.models import Event

class EventListView(ListView):
    model = Event

    def get_queryset(self):
        return Event.objects.filter(is_current=False)

    def get_ordering(self):
        return "when"
