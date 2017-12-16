from typing import List
from hello.models import *
from django.contrib.auth.models import User, Group

import uuid

def create_test_string(kind: str):
    return "%s_%s" % (kind, str(uuid.uuid4()).split('-')[0])


def create_test_players(count: int) -> List[Player]:
    for _ in range(0, count):
        User.objects.create(username=create_test_string('User'))

    return list(Player.objects.all())


def create_test_events(count: int) -> List[Event]:
    for _ in range(0, count):
        Event.objects.create(name=create_test_string('Event'), when='2017-12-15T23:59Z')

    return list(Event.objects.all())
