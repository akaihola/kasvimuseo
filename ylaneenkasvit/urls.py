from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponseRedirect
from photologue.views import GalleryArchiveIndexView
from ylaneenkasvit.dev_login import dev_login
from ylaneenkasvit.media import serve_media
import re

admin.autodiscover()

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # (r'^sentry/', include('sentry.web.urls')),
    # Photologue's own gallery index is a date archive with ``allow_empty``
    # off, so it raises ``Http404`` until the first gallery exists. Same path
    # and same URL name, declared before the include so it wins the match;
    # everything else photologue routes is left to the include below.
    url(r'^photologue/gallery/$',
        GalleryArchiveIndexView.as_view(allow_empty=True),
        name='pl-gallery-archive'),
    # ``namespace='photologue'`` is not a preference: photologue 3.0 moved its
    # own URLs into that namespace (upgrade plan Stage 4). Its ``urls.py``,
    # ``Gallery.get_absolute_url``, ``Photo.get_absolute_url`` and every
    # template it ships reverse ``photologue:<name>``, so without the namespace
    # every one of those raises ``NoReverseMatch``. The route above keeps the
    # bare ``pl-gallery-archive`` name as well, because
    # ``ylaneenkasvit/dashboard.py`` reverses it.
    url(r'^photologue/', include('photologue.urls', namespace='photologue')),
    url(r'^kasvimuseo/', include('kasvimuseo.urls')),
    # ``LoginView`` and ``LogoutView`` arrived at Django 1.11, and Django 2.1
    # deletes the ``login``/``logout`` function views they replace -- so
    # upgrade plan Stage 9 moves while both forms exist. Same templates, same
    # URL names; the templates move from the extra-context dict to
    # ``template_name`` arguments of ``as_view()``.
    url(r'^accounts/login/$',
        LoginView.as_view(template_name='jqm/login.html'),
        name='login'),
    url(r'^accounts/logout/$',
        LogoutView.as_view(template_name='jqm/logout.html'),
        name='logout'),

    url(r'^$', lambda request: HttpResponseRedirect('/admin/')),
]

# Password-free login for a development browser, and only where something has
# asked for it: ``settings.DEV_LOGIN`` comes from ``KASVIMUSEO_DEV_LOGIN``,
# which ``dev/kasvimuseo`` sets for the containers it starts and no deployment
# sets at all (issue 068). Without it this list has no such route and the path
# 404s like any other unknown one -- the gate is the absence of the URL, not a
# check inside the view, although ``ylaneenkasvit.dev_login`` makes that check
# too. The callable is imported rather than named as a string, because a string
# view is what Django 1.10 stops accepting (issue 022).
if settings.DEV_LOGIN:
    urlpatterns += [
        url(r'^dev-login/(?P<username>[^/]+)/$', dev_login, name='dev-login'),
    ]

# ``manage.py runserver`` serves ``STATIC_URL`` out of the staticfiles finders
# by itself, and nothing else does -- so under the gunicorn that
# ``dev/kasvimuseo app run`` now starts (issue 044) the admin would come up
# unstyled. Wire the same view up explicitly instead. This adds nothing unless
# ``DEBUG``: ``staticfiles_urlpatterns`` goes through
# ``django.conf.urls.static.static``, which returns an empty list otherwise, so
# production still serves ``/static/`` from its web server.
urlpatterns += staticfiles_urlpatterns()

# Uploaded photos, when this project is the one serving them: a single leading
# slash means ``MEDIA_URL`` is a path here, as the development and test
# settings have it. Production sets it to ``//media.kasvit.ambitone.com/``,
# another host, and gets no route at all. ``ylaneenkasvit.media`` explains the
# fallback the development case needs.
if (settings.MEDIA_URL.startswith('/')
        and not settings.MEDIA_URL.startswith('//')):
    urlpatterns += [
        url(r'^{0}(?P<path>.*)$'.format(
                re.escape(settings.MEDIA_URL.lstrip('/'))),
            serve_media,
            name='media'),
    ]
