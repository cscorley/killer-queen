
from django.views.generic import ListView
from hello.models import Season

class SeasonListView(ListView):
    model = Season

    def get_queryset(self):
        return Season.objects.order_by('-when')  # order by when?
