from django.contrib.auth.models import User, Group

from django.db import models
import trueskill

class Event(models.Model):
    name = models.CharField('name', max_length=255)
    created = models.DateTimeField('date created', auto_now_add=True)
    when = models.DateTimeField('event start time', auto_now_add=False)


class Player(models.Model):
    name = models.CharField('name', max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    trueskill_rating_mu = models.DecimalField('TrueSkill.Rating mu parameter',
                                              max_digits=10,
                                              decimal_places=4)
    trueskill_rating_sigma = models.DecimalField('TrueSkill.Rating sigma parameter',
                                                 max_digits=10,
                                                 decimal_places=4)


class Team(models.Model):
    name = models.CharField('name', max_length=255)
    created = models.DateTimeField('date created', auto_now_add=True)
    members = models.ManyToManyField(Player,
                                     through='TeamMembership',
                                     through_fields=('team', 'player'),
                                     )
    events = models.ManyToManyField(Event,
                                    through='EventTeam',
                                    through_fields=('team', 'event'),
                                    )


class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)


class EventTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class GameResult(models.Model):
    created = models.DateTimeField('date created', auto_now_add=True)
    blue = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='blue_result')
    gold = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='gold_result')
    blue_win_count = models.PositiveSmallIntegerField('Number of wins by the Blue team')
    gold_win_count = models.PositiveSmallIntegerField('Number of wins by the Gold team')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
