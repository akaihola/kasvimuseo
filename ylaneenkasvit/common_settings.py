# -*- encoding: utf-8 -*-

import os

from django.core.exceptions import ImproperlyConfigured

PROJECT_ROOT = os.environ.get(
    'KASVIMUSEO_SITE_ROOT', os.path.dirname(os.path.dirname(__file__)))
here = lambda *args: os.path.join(os.path.dirname(__file__), *args)


def secret_from_env(name):
    """Read a required environment variable or name the missing variable."""
    try:
        return os.environ[name]
    except KeyError:
        raise ImproperlyConfigured(
            '{0} is not set. Set {0} in the process environment and restart.'
            .format(name))


def hosts_from_env(name):
    """Read a required comma-separated list of allowed host names."""
    return [host.strip() for host in secret_from_env(name).split(',')
            if host.strip()]

# specify SITE_ROOT in site specific settings

# specify ADMINS and MANAGERS in site specific settings
ADMINS = (('Admin', 'admin@invalid'),)
MANAGERS = ADMINS

# specify database NAME, USER and PASSWORD in site specific settings
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'HOST': '/var/run/postgresql'}}

LANGUAGE_CODE = 'fi'
TIME_ZONE = 'Europe/Helsinki'
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

INSTALLED_APPS = (
    # Not for fixtures any more: the photo sizes that were its
    # ``initial_data.json`` live in the data migration
    # ``kasvimuseo/migrations/0002_photo_sizes.py`` now (issue 055, upgrade
    # plan Stage 5). What keeps this entry is ``ylaneenkasvit/locale/``: there is no
    # ``LOCALE_PATHS``, so those translations are found because the package is
    # an installed application. It defines no models.
    'ylaneenkasvit',
    'kasvimuseo',

    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',


    'jqm',
    # photologue 2.8's ``Gallery.photos`` is a ``SortedManyToManyField``, whose
    # admin widget renders ``sortedm2m/widget.html`` and loads
    # ``sortedm2m/widget.css``. Both come from the package's own ``templates/``
    # and ``static/``, which the app template loader and the staticfiles
    # finders only look in for an installed application.
    'sortedm2m',
    'photologue',

    # TODO: configure raven
)

# The Django 1.5 default, which the site has been running on implicitly, plus
# one entry. Spelled out because that default is withdrawn at Django 2.0 --
# ``MIDDLEWARE_CLASSES`` is gone from ``global_settings`` and ``MIDDLEWARE``
# defaults to ``[]``, so a project that never names its own middleware would
# quietly start with none: no sessions, no authentication, no CSRF (issue 019).
# Named ``MIDDLEWARE`` since Stage 8 of ``docs/upgrade-plan.rst``: Django 1.10
# reads the new name and runs the new-style protocol through it, every class
# below is Django's own and supports both styles, and 2.0 stops reading
# ``MIDDLEWARE_CLASSES`` at all.
#
# ``XFrameOptionsMiddleware`` is the one entry that is not in that default. It
# is what sets ``X-Frame-Options`` at all -- ``X_FRAME_OPTIONS`` below is read
# by nothing else -- and without it every page here, the admin and the label
# editor included, could be framed by any site and clicked through blind
# (issue 059). Last, so that it sees the finished response of everything above
# it, which is where Django's own ordering documentation puts it.
MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Written out although it is also the Django 1.5 default, for the reason 019
# spells out about ``MIDDLEWARE_CLASSES``: the default is not stable. Django
# 3.0 changes it to ``DENY``, so a project that leaves it unset gets a
# behaviour change out of an upgrade rather than out of a decision.
#
# ``SAMEORIGIN`` rather than ``DENY`` deliberately. The attack is a *foreign*
# page framing this one, and ``SAMEORIGIN`` refuses exactly that; ``DENY``
# additionally refuses this site framing itself, which buys no security and
# can break a widget -- the installed grappelli ships TinyMCE, whose editor is
# an iframe. The two public reports that *are* meant to be framed from another
# origin are exempted one by one in ``kasvimuseo/urls.py`` rather than by
# weakening this (issue 059).
X_FRAME_OPTIONS = 'SAMEORIGIN'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ``CSRF_COOKIE_HTTPONLY`` is deliberately absent, and this is the note that
# says so rather than an omission (issue 059). It had two reasons and has one
# left. The first is spent: Django 1.5 had no such setting, so writing it here
# would have been a setting Django ignores -- the silence issue 019 is about --
# and Django 1.6 defines it, defaulting to ``False`` (upgrade plan Stage 3).
# The second is the one that decides it now that the setting is live: the label
# editor's save reads the token out of ``document.cookie``
# (``kasvimuseo/templates/kasvimuseo/reports/planting-labels.html``), so an
# HttpOnly cookie would break Save for everyone. Moving that page to the
# ``{% csrf_token %}`` input it already renders is the prerequisite, and it is
# not this issue's change to make.
# ``kasvimuseo/tests/test_settings_cookie_security.py`` asserts both halves --
# the default, and that the issued cookie is one the page's JavaScript can
# read.

# JSON, which is what Django defaults to since 1.6 (upgrade plan Stage 3) and
# was not the default when this line was written: 1.5 serialized a session with
# ``django.contrib.sessions.serializers.PickleSerializer`` (issue 057). A
# session cookie's payload is unpickled once its HMAC verifies, and that HMAC is
# keyed on ``SECRET_KEY`` -- which this repository disclosed (issue 025) and
# which the running server has not been rotated off yet (issue 049). Under the
# pickle default that disclosure is arbitrary code execution in the application
# process; under JSON it is session forgery and nothing worse. Nothing this
# project puts in a session needs pickle: the auth keys are an integer primary
# key and a dotted path, and ``FallbackStorage`` hands the session an
# already-JSON-encoded string of messages. The line stays although it now
# names the default: 057's argument is about what this application must not
# serialize with, and a default is not a decision -- the same reason 019 writes
# out ``MIDDLEWARE`` and 059 writes out ``X_FRAME_OPTIONS``.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# One ``TEMPLATES`` entry replaces ``TEMPLATE_DIRS``,
# ``TEMPLATE_CONTEXT_PROCESSORS`` and ``TEMPLATE_DEBUG`` (upgrade plan Stage
# 6). Django 1.8 reads this setting; the three old names are deprecated.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Only this project's own templates. Photologue's are found by the
        # application template loader, which ``APP_DIRS`` turns on, so an
        # installed application's ``templates/`` directory needs no entry
        # here. There used to be a second entry naming photologue's templates
        # inside the virtualenv's ``site-packages`` by literal path: it wrote
        # the interpreter version into a settings file, and it had already
        # stopped resolving anywhere -- the container installs the
        # dependencies into the image and mounts the working copy at
        # ``/src``, which has no ``lib/`` (issue 024).
        'DIRS': [here('templates')],
        # The same two loaders Django 1.5's default ``TEMPLATE_LOADERS`` gave
        # this project: the filesystem loader for ``DIRS`` above, and the
        # application loader.
        'APP_DIRS': True,
        'OPTIONS': {
            # No ``debug`` entry: its default follows ``DEBUG``, which is
            # what the old ``TEMPLATE_DEBUG = DEBUG`` line said.
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'ylaneenkasvit.urls'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# specify in site specific settings:
#STATIC_URL = 'http://STATIC_URL/'
#GRAPPELLI_ADMIN_TITLE = u'GRAPPELLI_ADMIN_TITLE'
#MEDIA_URL = 'http://MEDIA_URL/'
#MEDIA_ROOT = os.path.join(SITE_ROOT, 'MEDIA_ROOT')

MEDIA_FALLBACK_URL = ''

GRAPPELLI_INDEX_DASHBOARD = 'ylaneenkasvit.dashboard.CustomIndexDashboard'
DATE_FORMAT = 'Y-m-d'

SITE_ID = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'stderr': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'stderr',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            # ``False`` where the stock block says ``True``, which is also what
            # Django's own ``DEFAULT_LOGGING`` says. With ``console`` named
            # here, propagating would hand the same record to the ``django``
            # logger's console handler and then to ``root`` below, and a
            # traceback would be printed two or three times under ``DEBUG``.
            # Nothing else is listening for these records.
            'propagate': False,
        },
        # The same treatment for the logger Django 1.6 added (upgrade plan
        # Stage 3), and it arrived with the same defect for the same reason:
        # ``DEFAULT_LOGGING`` gives ``django.security`` ``AdminEmailHandler``
        # alone and ``propagate: False``, so a ``SuspiciousOperation`` -- a bad
        # ``Host`` header against the ``ALLOWED_HOSTS`` 026 supplies, a
        # tampered signed cookie -- was mailed nowhere and written nowhere.
        # Named here rather than left to inherit, because what it inherits
        # depends on the ``django`` entry below: remove that and this logger
        # silently goes back to mailing ``localhost:25`` and nothing else.
        'django.security': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Django's ``DEFAULT_LOGGING`` -- applied before this dictionary, and
        # left in place by ``disable_existing_loggers: False`` -- puts a
        # console handler filtered by ``RequireDebugTrue`` on both of these.
        # Naming ``django`` also resets the loggers under it that this
        # dictionary does not name: ``dictConfig`` gives an existing child of a
        # configured logger back its defaults, so ``django.db.backends`` and
        # the rest reach ``root`` below rather than keeping handlers from a
        # pass this file cannot see.
        # With a root handler below, that handler is a second copy of every
        # warning whenever ``DEBUG`` is on: measured, and it is why the
        # ``django.conf.urls.defaults`` deprecation appeared twice on the
        # development server's output. Taking them off leaves ``root`` to print
        # each record once, the same way with ``DEBUG`` on or off.
        'django': {
            'handlers': [],
            'propagate': True,
        },
        'py.warnings': {
            'handlers': [],
            'propagate': True,
        },
    },
    # Everything that is not a request: management commands, the migration
    # tooling, a third-party package's own logger. ``WARNING`` rather than
    # ``INFO`` because this is a log nobody reads until something is wrong, and
    # ``django.request`` -- which logs every 404 at ``WARNING`` -- is handled
    # above at ``ERROR`` and does not reach here.
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}


DEBUG = bool(os.environ.get('KASVIMUSEO_DEBUG'))

DEV_LOGIN = bool(os.environ.get('KASVIMUSEO_DEV_LOGIN'))
