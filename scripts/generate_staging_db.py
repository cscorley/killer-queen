from django.contrib.auth.models import User, Group
from hello.models import Event, EventPlayer, Player


for event_id in range(1, 31):
    Event.objects.create(name='Event %d' % event_id, when='2017-12-15T23:59Z')

events = list(Event.objects.all())

for user_id in range(1, 31):
    User.objects.create(username='test_%d' % user_id)

players = list(Player.objects.all())

for player in players:
    player.trueskill_rating_exposure = player.user.id
    player.save()

for event in events:
    for player in players[:event.id]:
        EventPlayer.objects.create(event=event, player=player)


