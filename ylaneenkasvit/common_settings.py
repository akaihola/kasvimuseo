# -*- encoding: utf-8 -*-

import os

from django.core.exceptions import ImproperlyConfigured

PROJECT_ROOT = '/www/ylaneenkasvit'
here = lambda *args: os.path.join(os.path.dirname(__file__), *args)


def _from_env(name, source):
    """Return environment variable ``name``, or refuse to start without it.

    ``source`` says where the value comes from in production, so the message
    tells whoever hit it what to go and look at.
    """
    try:
        return os.environ[name]
    except KeyError:
        raise ImproperlyConfigured(
            '{0} is not set. This deployment reads its configuration from the'
            ' environment and has no default for it; set {0} in the process'
            ' environment (in production, uwsgi.ini writes it from {1}) and'
            ' start again.'.format(name, source))


def secret_from_env(name):
    """Return environment variable ``name``, or refuse to start without it.

    For a secret there is deliberately no default. A fallback would let a
    deployment that forgot to set the variable come up signing cookies and
    password-reset tokens with a value anybody who has ever cloned this
    repository knows, and it would do so silently -- see
    ``docs/issues/025-production-secret-key-and-database-password-are-committed.rst``.
    The test settings supply their own literals instead of calling this.
    """
    return _from_env(name, 'Ansible Vault')


def hosts_from_env(name):
    """Return the comma-separated host names in ``name``, or refuse to start.

    ``ALLOWED_HOSTS`` is the whole of Django's defence against a forged
    ``Host`` header once ``DEBUG`` is off, and it used to be set in no tracked
    file at all (issue 026). It is read the way the secrets are, and for the
    same reason: neither possible default is safe to have. An empty list makes
    every request a ``SuspiciousOperation``, so the site would be down without
    saying why, and ``['*']`` would switch the check off in exactly the
    deployment that forgot to configure it. A deployment that has not been told
    its host names therefore stops, naming the variable.

    The value is a comma-separated list, because a process environment holds
    strings: ``KASVIMUSEO_ALLOWED_HOSTS=kasvit.example.com,www.kasvit.example.com``.
    The test settings name their hosts literally instead of calling this.
    """
    # Not from the vault: host names are not secret, and keeping them in
    # ``ansible/vars/main.yml`` is what makes the deployment reproducible from
    # the tracked files.
    hosts = _from_env(name, 'ansible/vars/main.yml')
    return [host.strip() for host in hosts.split(',') if host.strip()]

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
    # Not for fixtures any more: ``initial_data.json`` moved to ``kasvimuseo``,
    # which has migrations, so South loads it after ``migrate`` instead of
    # ``syncdb`` trying it before photologue's tables exist (issue 055). What
    # keeps this entry is ``ylaneenkasvit/locale/``: there is no
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
    'django.contrib.staticfiles',

    # ``django_extensions`` is deliberately not here: it is a development tool
    # -- ``runserver_plus``, ``shell_plus`` -- that nothing in this repository
    # imports, and these settings are the ones production runs on (upgrade plan
    # Stage 0). ``local_settings.development.py`` appends it, so a development
    # checkout still has it and a production install does not have to install
    # it.
    'south',

    'jqm',
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

# JSON rather than the Django 1.5 default, which is
# ``django.contrib.sessions.serializers.PickleSerializer`` (issue 057). A
# session cookie's payload is unpickled once its HMAC verifies, and that HMAC is
# keyed on ``SECRET_KEY`` -- which this repository disclosed (issue 025) and
# which the running server has not been rotated off yet (issue 049). Under the
# pickle default that disclosure is arbitrary code execution in the application
# process; under JSON it is session forgery and nothing worse. Nothing this
# project puts in a session needs pickle: the auth keys are an integer primary
# key and a dotted path, and ``FallbackStorage`` hands the session an
# already-JSON-encoded string of messages. Django 1.6 makes this the default.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

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
