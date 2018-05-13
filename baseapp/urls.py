from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
admin.autodiscover()

import baseapp.settings as settings
import hello.views
import hello.views.events
import hello.views.seasons
import hello.api

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^account/$', hello.views.update_profile, name='account_update'),
    url(r'^accounts/signup/$', hello.views.signup, name='account_signup'),
    url(r'^top_players$', hello.views.top_players, name='top_players'),
    url(r'^events/(?P<event_id>\d+)/join$', hello.views.events.join, name='event_join'),
    url(r'^events/(?P<event_id>\d+)/result$', hello.views.events.result, name='event_result'),
    url(r'^events/(?P<event_id>\d+)/mix$', hello.views.events.mix, name='event_mix'),
    url(r'^events/current/$', hello.views.events.current, name='event_current'),
    url(r'^events/$', hello.views.events.EventListView.as_view()),
    url(r'^seasons/$', hello.views.seasons.SeasonListView.as_view()),
    path('admin/', admin.site.urls),
    url(r'^api/refresh_ratings$', hello.api.refresh_ratings, name='refresh_ratings'),
    url(r'^api/team_suggestions$', hello.api.team_suggestions, name='team_suggestions'),
    url(r'^api/user-autocomplete/$', hello.api.UserAutocomplete.as_view(), name='user-autocomplete'),
    url(r'^code-of-conduct$', hello.views.code_of_conduct, name='code-of-conduct'),
    url(r'^$', hello.views.index, name='index'),
]
