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
    # photologue 2.8 gave ``Photo`` and ``Gallery`` a ``sites`` many-to-many
    # and filters its own gallery and photo views by ``SITE_ID`` (upgrade plan
    # Stage 2), so the framework has to be installed and the setting has to
    # have a value -- see ``SITE_ID`` below. Nothing in this repository asks
    # for it otherwise: one site, one deployment per settings module.
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # ``django_extensions`` is deliberately not here: it is a development tool
    # -- ``runserver_plus``, ``shell_plus`` -- that nothing in this repository
    # imports, and these settings are the ones production runs on (upgrade plan
    # Stage 0). ``local_settings.development.py`` appends it, so a development
    # checkout still has it and a production install does not have to install
    # it.
    'south',

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
# Later stages of ``docs/upgrade-plan.rst`` edit this list, and it stays under
# the old name until Stage 8 (Django 1.10), where both spellings are honoured.
#
# ``XFrameOptionsMiddleware`` is the one entry that is not in that default. It
# is what sets ``X-Frame-Options`` at all -- ``X_FRAME_OPTIONS`` below is read
# by nothing else -- and without it every page here, the admin and the label
# editor included, could be framed by any site and clicked through blind
# (issue 059). Last, so that it sees the finished response of everything above
# it, which is where Django's own ordering documentation puts it.
MIDDLEWARE_CLASSES = (
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

# The deployment is TLS-only -- ``ansible/templates/nginx-site.conf.j2`` listens
# on 443 and answers port 80 with a 301 -- but a browser that reaches
# ``http://`` first sends its cookies *with the request that gets redirected*,
# so a typed address or an old bookmark leaks the logged-in session in
# cleartext before the 301 arrives. Django 1.5 defaults both of these to
# ``False``, which is the setting for a site that also serves plain HTTP; this
# one does not (issue 059).
#
# Development and the test suite do serve plain HTTP, so both override these to
# ``False``: ``local_settings.development.py`` for the development server and
# ``test_settings.py`` for the suite and the browser tests. Neither override is
# precautionary; both were measured, and what they prevent differs (issue 059).
# A client reaching this application by a name that is not loopback keeps no
# cookie at all over ``http://`` and simply cannot log in -- which is the
# development case, since the browser is often on another machine (issue 044).
# A client on ``127.0.0.1`` mostly can, because current browsers treat a
# loopback origin as trustworthy, but only mostly: without the override in
# ``test_settings`` one browser test fails, on a request Playwright makes
# outside the page. The production value is the one that lives here, so a
# deployment that has no override is secure rather than the other way round.
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
# out ``MIDDLEWARE_CLASSES`` and 059 writes out ``X_FRAME_OPTIONS``.
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

# The one site every deployment of these settings is. ``django.contrib.sites``
# arrived with photologue 2.8 (upgrade plan Stage 2) and its
# ``create_default_site`` receiver writes row 1 on the first ``syncdb``, so 1
# is the row that exists in a database bootstrapped here, in the test database
# and in the restored production dump alike -- ``django_site`` is a table this
# application had never had, so there was no other row it could be. Nothing
# here renders ``Site.domain``: what reads this setting is photologue, which
# filters its gallery and photo views by it, and the receiver that puts every
# saved photo on the current site.
SITE_ID = 1

# ``SOUTH_MIGRATION_MODULES`` is deliberately absent (upgrade plan Stage 2). It
# used to point photologue at ``ylaneenkasvit/external_migrations/photologue/``
# -- one local squashed ``0001_initial`` standing in for the package's whole
# history -- which meant photologue's own migrations could never run. That copy
# turned out to *be* photologue's own ``0001_initial``, so the
# ``south_migrationhistory`` row it left behind is the one photologue's history
# starts from and no faking was needed to adopt it; ``0002`` onwards are in the
# package. See ``dev/kasvimuseo db upgrade-photologue`` for the one migration
# in that history this project must not run, and why.


# Django's stock block with one handler added and one taken away: a stream
# handler, so that an unhandled exception is written down somewhere (issue
# 065), and no ``mail_admins``, because nothing was ever able to deliver what
# it sent (issue 066).
#
# What the stock block does on its own is send a 500's traceback to
# ``mail_admins`` and nowhere else. Django's own ``DEFAULT_LOGGING`` is applied
# first and puts a console handler on the ``django`` logger, but filtered by
# ``RequireDebugTrue`` -- so with ``DEBUG`` on, as production still runs
# (issue 051), the traceback does reach stderr and this looks fine. Turn
# ``DEBUG`` off, which is the whole of 051, and it stops: the filter drops the
# console copy, ``AdminEmailHandler`` mails ``localhost:25``, no MTA is
# installed by ``ansible/`` and no ``EMAIL_*`` setting points anywhere else,
# and ``mail.mail_admins(..., fail_silently=True)`` swallows the refused
# connection.
# The visitor gets ``templates/500.html`` and the traceback exists nowhere at
# all -- not in the response, not on stderr, not in a file. Measured, not
# reasoned: see the issue.
#
# So ``console`` is unconditional -- no ``RequireDebugTrue`` -- and goes on
# stderr, which is where both of this project's servers keep it: uWSGI writes
# it to ``/home/<app_user>/uwsgi.error.log`` (``logger = file:`` in
# ``ansible/roles/akaihola.uwsgi/templates/uwsgi.ini``) and the development
# gunicorn writes it to the container's output.
#
# There is deliberately no ``mail_admins`` handler, and this comment is the
# decision rather than the absence being an oversight (issue 066). Django's
# stock block has one -- ``AdminEmailHandler``, behind a ``RequireDebugFalse``
# filter -- and this project carried it until the maintainer ruled that
# ``uwsgi.error.log`` is enough: they are content to *look* at a 500 rather
# than be *told* about one.
#
# What it was doing until then was nothing, silently. Django's default is the
# SMTP backend on ``localhost:25``; nothing in ``ansible/`` installs an MTA, so
# the connection was refused, and ``AdminEmailHandler.emit`` passes
# ``fail_silently=True``, which swallows the refusal without an exception,
# without ``handleError`` and without a line in any log saying a handler had
# failed. The two alternatives to deleting it were an MTA on a host whose whole
# point is that it is small, and an ``EMAIL_HOST`` pointing at a relay that
# would have had to exist; both were declined.
#
# So stderr is the only place a production error is recorded, which is a
# smaller promise than the one this block used to make and a true one. If a
# notification is ever wanted, the handler comes back with an ``EMAIL_HOST``
# beside it -- and ``kasvimuseo/tests/test_settings_logging.py`` asserts the
# absence, so putting it back is a decision somebody takes rather than a
# default that creeps in.
#
# ``RequireDebugFalse`` goes with it: that filter existed only to keep the mail
# from being sent while ``DEBUG`` was on, and nothing else here uses it.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # uWSGI writes what a worker puts on stderr through verbatim, so the
        # timestamp and the logger name have to come from here or they are not
        # in ``uwsgi.error.log`` at all.
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
TEMPLATE_DEBUG = DEBUG

# The password-free ``/dev-login/<username>/`` route, off unless something asks
# for it (issue 068). ``dev/kasvimuseo`` sets the variable for the containers it
# starts and nothing else does, so a deployment -- which gets its environment
# from ``uwsgi.ini``, written by Ansible -- never registers the route at all.
#
# An environment variable rather than a line in
# ``ylaneenkasvit/development_settings.py``, which is where a development-only
# value has belonged since issue 069, because this one has to be switchable
# without editing a tracked file: it is a password-free admin login for anyone
# who can reach the port, so a session that should not offer it is
# ``KASVIMUSEO_DEV_LOGIN= dev/kasvimuseo app run``. The variable also reaches
# whichever settings module the harness runs, which is why ``test_settings``
# turns it off by hand rather than inheriting it.
#
# What it is deliberately not is a reading of ``DEBUG``. Production ran with
# ``DEBUG`` on behind an untracked ``local_settings.py`` for an unknown length
# of time (issue 051), so a gate that trusted it would have been open there.
DEV_LOGIN = bool(os.environ.get('KASVIMUSEO_DEV_LOGIN'))
