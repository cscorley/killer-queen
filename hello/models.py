from django.db import models
import trueskill

class Player(models.Model):
    name = models.CharField('name', max_length=255)
    email = models.EmailField('contact email')
    when = models.DateTimeField('date created', auto_now_add=True)
    trueskill_rating_mu = models.DecimalField('TrueSkill.Rating mu parameter')
    trueskill_rating_sigma = models.DecimalField('TrueSkill.Rating sigma parameter')


class Team(models.Model):
    name = models.CharField('name', max_length=255)
    members = models.ManyToManyField(Player,
                                     through='TeamMembership',
                                     through_fields=('team', 'player'),
                                     )


class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)


class GameResult(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)
    blue = models.ForeignKey(Team, on_delete=models.CASCADE)
    gold = models.ForeignKey(Team, on_delete=models.CASCADE)
    blue_win_count = models.PositiveSmallIntegerField('Number of wins by the Blue team')
    gold_win_count = models.PositiveSmallIntegerField('Number of wins by the Gold team')
