from typing import List, Tuple
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from hello.models import Player, Event, EventPlayer
from hello.views import index
from hello.api import team_suggestions_internal

from .data_fakers import create_test_players, create_test_events
import statistics
import math

from parameterized import parameterized

class TeamSuggestionsTests(TestCase):
    def setUp(self):
        self.TestPlayers = create_test_players(10)
        self.TestEvents = create_test_events(1)

        self.assertEqual(10, len(self.TestPlayers))
        self.assertEqual(1, len(self.TestEvents))

        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_team_suggestion_no_registered_players(self):
        event: Event = self.TestEvents[0]
        self.assertEqual(list(), team_suggestions_internal(event, 5, 2))

    def test_team_suggestion_top_2_diff(self):
        event: Event = self.TestEvents[0]
        for rating, player in enumerate(self.TestPlayers):
            player.trueskill_rating_exposure = rating
            player.save()
            EventPlayer.objects.create(event=event, player=player)

        ranked_players = sorted(self.TestPlayers, key=lambda player: player.trueskill_rating_exposure, reverse=True)
        self.assertEqual(9, ranked_players[0].trueskill_rating_exposure)

        suggestions: List[List[Player]] = team_suggestions_internal(event, 5, 2)
        team_0_mean = statistics.mean([x.trueskill_rating_exposure for x in suggestions[0]])
        team_1_mean = statistics.mean([x.trueskill_rating_exposure for x in suggestions[1]])
        self.assertTrue(abs(team_0_mean - team_1_mean) < 0.5)
        self.assertEqual(9, suggestions[0][0].trueskill_rating_exposure)
        self.assertEqual(8, suggestions[1][0].trueskill_rating_exposure)
        #self.assertEqual(0, suggestions[0][-1].trueskill_rating_exposure)
        #self.assertEqual(list(), suggestions)

    @parameterized.expand([(3, ), (5, ), (7, ), (9, )])
    def test_team_suggestion_odd_players_included(self, num_players):
        event: Event = self.TestEvents[0]
        for rating, player in enumerate(self.TestPlayers[:num_players]):
            player.trueskill_rating_exposure = rating
            player.save()
            EventPlayer.objects.create(event=event, player=player)

        ranked_players = sorted(self.TestPlayers, key=lambda player: player.trueskill_rating_exposure, reverse=True)

        suggestions: List[List[Player]] = team_suggestions_internal(event, 5, 2)
        self.assertEqual(num_players, sum(len(x) for x in suggestions))
        #self.assertEqual(0, suggestions[0][-1].trueskill_rating_exposure)
        #self.assertEqual(list(), suggestions)

    def test_view(self):
        # Create an instance of a GET request.
        request = self.factory.get('/')
        request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = index(request)
        self.assertEqual(response.status_code, 200)

