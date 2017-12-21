from django.db import models


from .enums import TournamentStyle
from .fields import EnumField

from .player import Player
from .team import Team

class Event(models.Model):
    name = models.CharField('name', max_length=255)
    created = models.DateTimeField('date created', auto_now_add=True)
    when = models.DateTimeField('event start time', auto_now_add=False)
    timezone = models.CharField('timezone', max_length=50, default="America/New_York")
    players = models.ManyToManyField(Player,
                                     through='EventPlayer',
                                     through_fields=('event', 'player'),
                                     )
    teams = models.ManyToManyField(Team,
                                   through='EventTeam',
                                   through_fields=('event', 'team'),
                                   )

    is_current = models.BooleanField('Determines whether this is a current event', default=False)
    is_active = models.BooleanField('Determines whether this is an active event', default=True)

    tournament_style = EnumField(verbose_name='tournament style',
                                 enum_class=TournamentStyle,
                                 default=int(TournamentStyle.ROUND_ROBIN))

    def __str__(self) -> str:
        return "%s (%s)" % (self.name, str(self.when))


class EventTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'event')

    def __str__(self) -> str:
        return "%s (%s)" % (self.team.name, self.event.name)


class EventPlayer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player', 'event')

    def __str__(self) -> str:
        return "%s (%s)" % (self.player.user.username, self.event.name)


class GameResult(models.Model):
    created = models.DateTimeField('date created', auto_now_add=True)
    blue = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='blue_result')
    gold = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='gold_result')
    blue_win_count = models.PositiveSmallIntegerField('Number of wins by the Blue team')
    gold_win_count = models.PositiveSmallIntegerField('Number of wins by the Gold team')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        if self.event:
            return "%s (%d) vs %s (%d) at %s" % (self.blue.name, self.blue_win_count, self.gold.name, self.gold_win_count, self.event.name)
        else:
            return "%s (%d) vs %s (%d)" % (self.blue.name, self.blue_win_count, self.gold.name, self.gold_win_count)