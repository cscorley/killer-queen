from django.db import models

from .player import Player

class Team(models.Model):
    name = models.CharField('name', max_length=255)
    created = models.DateTimeField('date created', auto_now_add=True)
    members = models.ManyToManyField(Player,
                                     through='TeamMembership',
                                     through_fields=('team', 'player'),
                                     )

    def __str__(self) -> str:
        return self.name


class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'player')

    def __str__(self) -> str:
        return "%s (%s)" % (self.team.name, self.player.user.username)
