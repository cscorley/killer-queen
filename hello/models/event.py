from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator

from .enums import TournamentStyle
from .fields import EnumField

from .player import Player
from .team import Team
from .season import Season

import itertools
import trueskill
from hello.trueskill_environment import skill_env

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

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='events')

    is_current = models.BooleanField('Determines whether this is a current event', default=False)
    is_active = models.BooleanField('Determines whether this is an active event', default=True)

    tournament_url = models.CharField('tournament url', max_length=255)
    token = models.CharField('Secret token', max_length=50, default='')

    def __str__(self) -> str:
        return "%s (%s, %s)" % (self.name, self.season.name, str(self.when))


class EventTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'event')

    def __str__(self) -> str:
        return "%s (%s)" % (self.team.name, self.event.name)


class EventPlayer(models.Model):
    created = models.DateTimeField('registration time', auto_now_add=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player', 'event')
        ordering = ['created']

    def __str__(self) -> str:
        return "%s (%s)" % (self.player.user.username, self.event.name)

def get_win(letter: str):
    if letter == 'B':
        return [0, 1]
    elif letter == 'G':
        return [1, 0]
    else:
        return None

win_validator = RegexValidator(r'^[BGbg]*$', 'Only B or G characters are allowed.')

class GameResult(models.Model):
    created = models.DateTimeField('date created', auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    gold = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='gold_result')
    blue = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='blue_result')
    gold_win_count = models.PositiveSmallIntegerField('Number of wins by the Gold team', default=0)
    blue_win_count = models.PositiveSmallIntegerField('Number of wins by the Blue team', default=0)
    win_order = models.CharField('Win order', max_length=20, default="", validators=[win_validator])
    contributes_to_season_score = models.BooleanField(default=True)

    def __str__(self) -> str:
        if self.event:
            return "%s (%d) vs %s (%d) at %s" % (self.blue.name, self.blue_win_count, self.gold.name, self.gold_win_count, self.event.name)
        else:
            return "%s (%d) vs %s (%d)" % (self.blue.name, self.blue_win_count, self.gold.name, self.gold_win_count)

    def process(self) -> None:
        blue: List[Player] = list(self.blue.members.all())
        gold: List[Player] = list(self.gold.members.all())

        blue_ratings: List[trueskill.Rating] = [x.get_rating() for x in blue]
        gold_ratings: List[trueskill.Rating] = [x.get_rating() for x in gold]

        results: List[List[int]]

        if len(self.win_order) != 0:
            results = [get_win(win) for win in self.win_order]

            if self.blue_win_count == 0 and self.gold_win_count == 0:
                self.win_order = self.win_order.upper()
                self.blue_win_count = self.win_order.count('B')
                self.gold_win_count = self.win_order.count('G')
                self.save()
        else:
            blue_wins_iter = iter([get_win('B')] * self.blue_win_count)
            gold_wins_iter = iter([get_win('G')] * self.gold_win_count)

            # cycle between blue and gold wins so scores are updated somewhat fairly since we don't
            # track literal win order
            alternating = list()

            for i in itertools.cycle([blue_wins_iter, gold_wins_iter]):
                try:
                    alternating.append(next(i))
                except StopIteration:
                    break

            # since one team may have won a bunch more than the other, just put any that weren't able
            #  to be alternated at the end
            remainder = list(itertools.chain(blue_wins_iter, gold_wins_iter))

            results = list(alternating + remainder)

            # need to generate win_order results
            for win in results:
                if win == [0, 1]:
                    # blue win
                    self.win_order += 'B'
                elif win == [1, 0]:
                    # gold win
                    self.win_order += 'G'
                else:
                    # unknown
                    self.win_order += 'E'

            if len(self.win_order) != 0:
                self.save()

        for win in results:
            blue_ratings, gold_ratings = skill_env.rate([blue_ratings, gold_ratings], ranks=win)

        for player, rating in zip(blue, blue_ratings):
            player.update_rating(rating, self.blue_win_count, self.gold_win_count)

        for player, rating in zip(gold, gold_ratings):
            player.update_rating(rating, self.gold_win_count, self.blue_win_count)

@receiver(post_save, sender=GameResult)
def process_game_result(sender, instance, created, **kwargs):
    if created:
        instance.process()
