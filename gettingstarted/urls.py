from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

import hello.views
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
    url(r'^signup/$', hello.views.signup, name='signup'),
    url(r'^events/(?P<event_id>\d+)/join$', hello.views.event_join, name='event_join'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/refresh_ratings$', hello.api.refresh_ratings, name='refresh_ratings'),
    url(r'^api/team_suggestions$', hello.api.team_suggestions, name='team_suggestions'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns += router.urls
