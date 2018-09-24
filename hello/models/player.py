from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

import trueskill
from hello.trueskill_environment import skill_env, default_mu, default_sigma, default_exposure

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trueskill_rating_mu = models.FloatField('TrueSkill.Rating mu parameter',
                                            default=default_mu)
    trueskill_rating_sigma = models.FloatField('TrueSkill.Rating sigma parameter',
                                               default=default_sigma)
    trueskill_rating_exposure = models.FloatField('TrueSkill.Rating exposure.  Use this for sorting',
                                                  default=default_exposure)
    map_wins = models.PositiveIntegerField('Number of wins by map', default=0)
    map_losses = models.PositiveIntegerField('Number of losses by map', default=0)
    match_wins = models.PositiveIntegerField('Number of wins by match', default=0)
    match_losses = models.PositiveIntegerField('Number of losses by match', default=0)

    wants_queen = models.BooleanField('Would like to play Queen', default=False)

    def update_rating(self, rating: trueskill.Rating, map_wins: int, map_losses: int) -> None:
        self.trueskill_rating_mu = rating.mu
        self.trueskill_rating_sigma = rating.sigma
        self.trueskill_rating_exposure = trueskill.expose(rating)
        self.map_wins = self.map_wins + map_wins
        self.map_losses = self.map_losses + map_losses

        if map_wins > map_losses:
            self.match_wins = self.match_wins + 1
        elif map_wins < map_losses:
            self.match_losses = self.match_losses + 1

        self.save()

    def clear_stats(self):
        self.trueskill_rating_mu = default_mu
        self.trueskill_rating_sigma = default_sigma
        self.trueskill_rating_exposure = default_exposure
        self.map_wins = 0
        self.map_losses = 0
        self.match_wins = 0
        self.match_losses = 0

        self.save()


    def get_rating(self) -> trueskill.Rating:
        return skill_env.Rating(self.trueskill_rating_mu, self.trueskill_rating_sigma)

    def __str__(self) -> str:
        return "%s (%s, e=%.3f, m=%.3f, s=%.3f, q=%i)" % (self.user.get_full_name(),
                                                    self.user.username,
                                                    self.trueskill_rating_exposure,
                                                    self.trueskill_rating_mu,
                                                    self.trueskill_rating_sigma,
                                                    self.wants_queen)

    def confidence(self):
        return min(100.0, 100 * (1.0 - self.trueskill_rating_sigma / default_sigma))


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)

    instance.player.save()

def user_str(self):
    return "%s (%s)" % (self.get_full_name(), self.username)

User.add_to_class("__str__", user_str)
