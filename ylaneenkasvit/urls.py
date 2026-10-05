from django.conf import settings
from django.urls import include, re_path
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
    re_path(r'^grappelli/', include('grappelli.urls')),
    # ``admin.site.urls`` is a 3-tuple, which ``include()`` stops accepting
    # at Django 2.0 (upgrade plan Stage 11); the tuple is passed directly.
    re_path(r'^admin/', admin.site.urls),
    # (r'^sentry/', include('sentry.web.urls')),
    # Photologue's own gallery index is a date archive with ``allow_empty``
    # off, so it raises ``Http404`` until the first gallery exists. Same path
    # and same URL name, declared before the include so it wins the match;
    # everything else photologue routes is left to the include below.
    re_path(r'^photologue/gallery/$',
        GalleryArchiveIndexView.as_view(allow_empty=True),
        name='pl-gallery-archive'),
    # ``namespace='photologue'`` is not a preference: photologue 3.0 moved its
    # own URLs into that namespace (upgrade plan Stage 4). Its ``urls.py``,
    # ``Gallery.get_absolute_url``, ``Photo.get_absolute_url`` and every
    # template it ships reverse ``photologue:<name>``, so without the namespace
    # every one of those raises ``NoReverseMatch``. The route above keeps the
    # bare ``pl-gallery-archive`` name as well, because
    # ``ylaneenkasvit/dashboard.py`` reverses it.
    re_path(r'^photologue/', include('photologue.urls', namespace='photologue')),
    re_path(r'^kasvimuseo/', include('kasvimuseo.urls')),
    # ``LoginView`` and ``LogoutView`` arrived at Django 1.11, and Django 2.1
    # deletes the ``login``/``logout`` function views they replace -- so
    # upgrade plan Stage 9 moves while both forms exist. Same templates, same
    # URL names; the templates move from the extra-context dict to
    # ``template_name`` arguments of ``as_view()``.
    re_path(r'^accounts/login/$',
        LoginView.as_view(template_name='jqm/login.html'),
        name='login'),
    re_path(r'^accounts/logout/$',
        LogoutView.as_view(template_name='jqm/logout.html'),
        name='logout'),

    re_path(r'^$', lambda request: HttpResponseRedirect('/admin/')),
]

if settings.DEV_LOGIN:
    urlpatterns += [
        re_path(r'^dev-login/(?P<username>[^/]+)/$', dev_login, name='dev-login'),
    ]

urlpatterns += staticfiles_urlpatterns()

if (settings.MEDIA_URL.startswith('/')
        and not settings.MEDIA_URL.startswith('//')):
    urlpatterns += [
        re_path(r'^{0}(?P<path>.*)$'.format(
                re.escape(settings.MEDIA_URL.lstrip('/'))),
            serve_media,
            name='media'),
    ]
