from dal import autocomplete
from django.db.models import Q

from django.contrib.auth.models import User
import logging

logger = logging.getLogger('hello')

class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.all().order_by('username')

        if self.q:
            qs = qs.filter(
                    Q(username__icontains=self.q) |
                    Q(first_name__icontains=self.q) |
                    Q(last_name__icontains=self.q)
                    )

        return qs