from django.conf.urls.defaults import *
from django.contrib import admin
from django.http import HttpResponseRedirect
import grappelli
import os

admin.autodiscover()

urlpatterns = patterns('',
    (r'^grappelli/', include('grappelli.urls')),
    (r'^media/grappelli/(?P<path>.*)', 'django.views.static.serve',
     {'document_root': os.path.join(os.path.dirname(grappelli.__file__), 'media')}),
    (r'^admin/', include(admin.site.urls)),
    (r'^sentry/', include('sentry.urls')),
    (r'^$', lambda request: HttpResponseRedirect('/admin/')),
)
