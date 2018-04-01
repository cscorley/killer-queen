from django.db import models

import statistics

from .player import Player

class Team(models.Model):
    name = models.CharField('name', max_length=255, unique=False)
    created = models.DateTimeField('date created', auto_now_add=True)
    members = models.ManyToManyField(Player,
                                     through='TeamMembership',
                                     through_fields=('team', 'player'),
                                     )

    def __str__(self) -> str:
        return "%s (%s)" % (self.name, self.id)

    def get_rating_mean(self) -> float:
        players = list(self.members.all())
        if players:
            return statistics.mean([x.trueskill_rating_exposure if x else 0 for x in players])
        else:
            return 0.0


class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'player')

    def __str__(self) -> str:
        return "%s (%s)" % (self.team.name, self.player.user.username)
