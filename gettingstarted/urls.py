from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import hello.views
import hello.api

urlpatterns = [
    url(r'^$', hello.views.index, name='index'),
    url(r'^db', hello.views.db, name='db'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(hello.api.v1.urls)), # http://localhost:5000/api/v1/?format=json
]
