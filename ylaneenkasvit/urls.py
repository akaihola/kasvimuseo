from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from photologue.views import GalleryArchiveIndexView
import grappelli
import os
import re

admin.autodiscover()

urlpatterns = patterns(
    '',

    (r'^grappelli/', include('grappelli.urls')),
    (r'^media/grappelli/(?P<path>.*)', 'django.views.static.serve',
     {'document_root': os.path.join(os.path.dirname(grappelli.__file__),
                                    'media')}),
    (r'^admin/', include(admin.site.urls)),
    # (r'^sentry/', include('sentry.web.urls')),
    # Photologue's own gallery index is a date archive with ``allow_empty``
    # off, so it raises ``Http404`` until the first gallery exists. Same path
    # and same URL name, declared before the include so it wins the match;
    # everything else photologue routes is left to the include below.
    url(r'^photologue/gallery/$',
        GalleryArchiveIndexView.as_view(allow_empty=True),
        name='pl-gallery-archive'),
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

# Uploaded photos, when this project is the one serving them: a single leading
# slash means ``MEDIA_URL`` is a path here, as the development and test
# settings have it. Production sets it to ``//media.kasvit.ambitone.com/``,
# another host, and gets no route at all. ``ylaneenkasvit.media`` explains the
# fallback the development case needs.
if (settings.MEDIA_URL.startswith('/')
        and not settings.MEDIA_URL.startswith('//')):
    urlpatterns += patterns(
        '',
        url(r'^{0}(?P<path>.*)$'.format(
                re.escape(settings.MEDIA_URL.lstrip('/'))),
            'ylaneenkasvit.media.serve_media',
            name='media'),
    )
