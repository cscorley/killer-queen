from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path

import baseapp.settings as settings
import hello.api
import hello.views
import hello.views.events
import hello.views.seasons

admin.autodiscover()


urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^account/$', hello.views.update_profile, name='account_update'),
    url(r'^accounts/signup/$', hello.views.signup, name='account_signup'),
    url(r'^top_players$', hello.views.top_players, name='top_players'),
    url(r'^events/(?P<event_id>\d+)/join$', hello.views.events.join, name='event_join'),
    url(r'^events/(?P<event_id>\d+)/result$', hello.views.events.result, name='event_result'),
    url(r'^events/(?P<event_id>\d+)/mix$', hello.views.events.mix, name='event_mix'),
    url(r'^events/(?P<event_id>\d+)/start$', hello.views.events.start, name='event_start'),
    url(r'^events/(?P<event_id>\d+)/kiosk$', hello.views.events.kiosk, name='event_kiosk'),
    url(r'^events/(?P<event_id>\d+)/oldkiosk$', hello.views.events.old_kiosk, name='event_old_kiosk'),
    url(r'^events/current/$', hello.views.events.current, name='event_current'),
    url(r'^events/current-kiosk$', hello.views.events.current_kiosk, name='event_current_kiosk'),
    url(r'^events/$', hello.views.events.EventListView.as_view()),
    url(r'^kiosk$', hello.views.kiosk, name='general_kiosk'),
    url(r'^seasons/$', hello.views.seasons.SeasonListView.as_view()),
    url(r'^seasons/(?P<season_id>\d+)/top_players$', hello.views.seasonal_top_players, name='seasonal_top_players'),
    path('admin/', admin.site.urls),
    url(r'^api/refresh_ratings$', hello.api.refresh_ratings, name='refresh_ratings'),
    url(r'^api/team_suggestions$', hello.api.team_suggestions, name='team_suggestions'),
    url(r'^api/user-autocomplete/$', hello.api.UserAutocomplete.as_view(), name='user-autocomplete'),
    url(r'^api/cab/bracket$', hello.api.cab.bracket, name='cab-bracket'),
    url(r'^api/cab/goldonleft$', hello.api.cab.goldonleft, name='cab-goldonleft'),
    url(r'^code-of-conduct$', hello.views.code_of_conduct, name='code-of-conduct'),
    url(r'^$', hello.views.index, name='index'),
]
