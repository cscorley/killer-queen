from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

import trueskill
from hello.trueskill_environment import skill_env, default_mu, default_sigma, default_exposure
from .enums import TournamentStyle
from .fields import EnumField

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trueskill_rating_mu = models.FloatField('TrueSkill.Rating mu parameter',
                                            default=default_mu)
    trueskill_rating_sigma = models.FloatField('TrueSkill.Rating sigma parameter',
                                               default=default_sigma)
    trueskill_rating_exposure = models.FloatField('TrueSkill.Rating exposure.  Use this for sorting',
                                                  default=default_exposure)

    def update_rating(self, rating: trueskill.Rating) -> None:
        self.trueskill_rating_mu = rating.mu
        self.trueskill_rating_sigma = rating.sigma
        self.trueskill_rating_exposure = trueskill.expose(rating)
        self.save()

    def get_rating(self) -> trueskill.Rating:
        return skill_env.Rating(self.trueskill_rating_mu, self.trueskill_rating_sigma)

    def __str__(self) -> str:
        return "%s (%s, rating=%d)" % (self.user.get_full_name(), self.user.username, self.trueskill_rating_exposure)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)

    instance.player.save()

class Team(models.Model):
    name = models.CharField('name', max_length=255)
    created = models.DateTimeField('date created', auto_now_add=True)
    members = models.ManyToManyField(Player,
                                     through='TeamMembership',
                                     through_fields=('team', 'player'),
                                     )

    def __str__(self) -> str:
        return self.name

class Event(models.Model):
    name = models.CharField('name', max_length=255)
    created = models.DateTimeField('date created', auto_now_add=True)
    when = models.DateTimeField('event start time', auto_now_add=False)
    players = models.ManyToManyField(Player,
                                     through='EventPlayer',
                                     through_fields=('event', 'player'),
                                     )
    teams = models.ManyToManyField(Team,
                                   through='EventTeam',
                                   through_fields=('event', 'team'),
                                   )

    is_current = models.BooleanField('Determines whether this is a current event', default=False)
    tournament_style = EnumField(verbose_name='tournament style',
                                 enum_class=TournamentStyle,
                                 default=int(TournamentStyle.ROUND_ROBIN))

    def __str__(self) -> str:
        return "%s (%s)" % (self.name, str(self.when))



class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'player')

    def __str__(self) -> str:
        return "%s (%s)" % (self.team.name, self.player.user.username)


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