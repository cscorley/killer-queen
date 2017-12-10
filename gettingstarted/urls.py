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

urlpatterns = [
    url(r'^$', hello.views.index, name='index'),
    url(r'^db', hello.views.db, name='db'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
