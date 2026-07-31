# -*- encoding: utf-8 -*-

import os

from django.core.exceptions import ImproperlyConfigured

PROJECT_ROOT = '/www/ylaneenkasvit'
here = lambda *args: os.path.join(os.path.dirname(__file__), *args)


def secret_from_env(name):
    """Return environment variable ``name``, or refuse to start without it.

    For a secret there is deliberately no default. A fallback would let a
    deployment that forgot to set the variable come up signing cookies and
    password-reset tokens with a value anybody who has ever cloned this
    repository knows, and it would do so silently -- see
    ``docs/issues/025-production-secret-key-and-database-password-are-committed.rst``.
    The test settings supply their own literals instead of calling this.
    """
    try:
        return os.environ[name]
    except KeyError:
        raise ImproperlyConfigured(
            '{0} is not set. This deployment reads its secrets from the'
            ' environment and has no default for them; set {0} in the'
            ' process environment (in production, uwsgi.ini writes it from'
            ' Ansible Vault) and start again.'.format(name))

# specify SITE_ROOT in site specific settings

# specify ADMINS and MANAGERS in site specific settings
ADMINS = (('Admin', 'admin@invalid'),)
MANAGERS = ADMINS

# specify database NAME, USER and PASSWORD in site specific settings
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'HOST': '/var/run/postgresql'}}

LANGUAGE_CODE = 'fi'
TIME_ZONE = 'Europe/Helsinki'
USE_TZ = True

INSTALLED_APPS = (
    'ylaneenkasvit',  # for fixtures
    'kasvimuseo',

    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'django_extensions',
    'gunicorn',
    'south',

    'indexer',
    'jqm',
    'paging',
    'photologue',

    # TODO: configure raven
)

# A verbatim copy of the Django 1.5 default, which the site has been running on
# implicitly. Spelled out because that default is withdrawn at Django 2.0 --
# ``MIDDLEWARE_CLASSES`` is gone from ``global_settings`` and ``MIDDLEWARE``
# defaults to ``[]``, so a project that never names its own middleware would
# quietly start with none: no sessions, no authentication, no CSRF (issue 019).
# Later stages of ``docs/upgrade-plan.rst`` edit this list, and it stays under
# the old name until Stage 8 (Django 1.10), where both spellings are honoured.
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

# Only this project's own templates. Photologue's are found by the app
# template loader, which is in Django's default ``TEMPLATE_LOADERS`` and which
# this project does not override, so an installed application's ``templates/``
# directory needs no entry here. There used to be a second entry naming
# photologue's templates inside the virtualenv's ``site-packages`` by literal
# path: it wrote the interpreter version into a settings file, and it had
# already stopped resolving anywhere -- the container installs the dependencies
# into the image and mounts the working copy at ``/src``, which has no ``lib/``
# (issue 024).
TEMPLATE_DIRS = (here('templates'),)

ROOT_URLCONF = 'ylaneenkasvit.urls'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# specify in site specific settings:
#STATIC_URL = 'http://STATIC_URL/'
#ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'
#GRAPPELLI_ADMIN_TITLE = u'GRAPPELLI_ADMIN_TITLE'
#MEDIA_URL = 'http://MEDIA_URL/'
#MEDIA_ROOT = os.path.join(SITE_ROOT, 'MEDIA_ROOT')

# Where to send a request for a media file this installation does not have.
# Only consulted when ``MEDIA_URL`` is a local path, which is what makes
# ``ylaneenkasvit.media.serve_media`` a route at all; the development settings
# point it at the production media host so a fresh clone shows photos it has
# not downloaded. Empty means a missing file is a 404, which is what production
# and the test suite want.
MEDIA_FALLBACK_URL = ''

GRAPPELLI_INDEX_DASHBOARD = 'ylaneenkasvit.dashboard.CustomIndexDashboard'
DATE_FORMAT = 'Y-m-d'

SOUTH_MIGRATION_MODULES = {
    'photologue': 'ylaneenkasvit.external_migrations.photologue',
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


DEBUG = bool(os.environ.get('KASVIMUSEO_DEBUG'))
TEMPLATE_DEBUG = DEBUG
