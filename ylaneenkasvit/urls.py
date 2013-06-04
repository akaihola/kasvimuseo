from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from django.http import HttpResponseRedirect
import grappelli
import os

admin.autodiscover()

urlpatterns = patterns(
    '',

    (r'^grappelli/', include('grappelli.urls')),
    (r'^media/grappelli/(?P<path>.*)', 'django.views.static.serve',
     {'document_root': os.path.join(os.path.dirname(grappelli.__file__),
                                    'media')}),
    (r'^admin/', include(admin.site.urls)),
    # (r'^sentry/', include('sentry.web.urls')),
    (r'^photologue/', include('photologue.urls')),
    (r'^kasvimuseo/', include('kasvimuseo.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        dict(template_name='jqm/login.html'),
        name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        dict(template_name='jqm/logout.html'),
        name='logout'),

    (r'^$', lambda request: HttpResponseRedirect('/admin/')),
)
