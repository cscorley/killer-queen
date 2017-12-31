from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

import baseapp.settings as settings
import hello.views
import hello.views.events
import hello.api

from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'users', hello.api.UserViewSet)
router.register(r'groups', hello.api.GroupViewSet)
router.register(r'players', hello.api.PlayerViewSet)
router.register(r'teams', hello.api.TeamViewSet)
router.register(r'teammemberships', hello.api.TeamMembershipViewSet)
router.register(r'gameresults', hello.api.GameResultViewSet)
router.register(r'events', hello.api.EventViewSet)
router.register(r'eventteams', hello.api.EventTeamViewSet)
router.register(r'eventplayers', hello.api.EventPlayerViewSet)

urlpatterns = [
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^account/$', hello.views.UserUpdateView.as_view(), name='account_update'),
    url(r'^account/signup/$', hello.views.signup, name='account_signup'),
    url(r'^events/(?P<event_id>\d+)/join$', hello.views.events.join, name='event_join'),
    url(r'^events/(?P<event_id>\d+)/result$', hello.views.events.result, name='event_result'),
    url(r'^events/current/$', hello.views.events.current, name='event_current'),
    url(r'^events/$', hello.views.events.EventListView.as_view()),
    url(r'^admin/', admin.site.urls),
    url(r'^api/refresh_ratings$', hello.api.refresh_ratings, name='refresh_ratings'),
    url(r'^api/team_suggestions$', hello.api.team_suggestions, name='team_suggestions'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/user-autocomplete/$', hello.api.UserAutocomplete.as_view(), name='user-autocomplete'),
    url(r'^$', hello.views.index, name='index'),
]

urlpatterns += [url(r'^api/', include(router.urls))]
