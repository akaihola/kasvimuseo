# -*- encoding: utf-8 -*-
"""Settings for the automated tests.

Deliberately built on ``common_settings`` rather than on
``ylaneenkasvit_settings``, so the suite does not depend on the untracked
``local_settings.py`` of whoever runs it. Database connection details come from
the same environment variables ``dev/kasvimuseo`` exports.
"""

import os

from .common_settings import *  # noqa

# The site settings read the key from ``KASVIMUSEO_SECRET_KEY`` and refuse to
# start without it (issue 025). The suite signs nothing that outlives it, so it
# supplies its own literal instead and needs no variable set.
SECRET_KEY = 'test'

# Named here rather than read from ``KASVIMUSEO_ALLOWED_HOSTS`` (issue 026), for
# the same reason as the key above: nothing has to be set to run the suite. The
# suite itself never reads this -- Django 1.5's ``setup_test_environment``
# replaces ``ALLOWED_HOSTS`` with ``['*']`` for the duration of a test run
# (``django/test/utils.py``) -- but the browser tests serve these same settings
# from gunicorn, outside that, and reach it on ``127.0.0.1`` (issue 017).
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# South migrates apps alphabetically, so ``kasvimuseo`` runs before
# ``photologue`` and migration 0014 fails on the foreign key to
# ``photologue_photo``. With this off, South leaves the test database to
# ``syncdb``, which builds every table straight from the models.
SOUTH_TESTS_MIGRATE = False

DATABASES['default'].update({  # noqa: F405
    'NAME': os.environ.get('KASVIMUSEO_DB_NAME', 'ylaneenkasvit'),
    'USER': os.environ.get('KASVIMUSEO_DB_USER', 'ylaneenkasvit'),
    # Empty rather than any real password: the local development cluster
    # trusts local connections, and a default here is exactly how the
    # production password used to reach a tracked file (issue 025).
    'PASSWORD': os.environ.get('KASVIMUSEO_DB_PASSWORD', ''),
    'PORT': os.environ.get('KASVIMUSEO_DB_PORT', ''),
    # Lets concurrent test runs against one cluster use separate databases.
    'TEST_NAME': 'test_{0}{1}'.format(
        os.environ.get('KASVIMUSEO_DB_NAME', 'ylaneenkasvit'),
        os.environ.get('KASVIMUSEO_TEST_SUFFIX', '')),
})

# ``common_settings`` marks both cookies ``Secure``, because production is
# TLS-only (issue 059). Nothing here is: the suite's own client speaks to
# ``http://testserver`` and the browser tests serve these same settings from
# gunicorn on ``http://127.0.0.1`` and log into the admin. Chromium treats that
# loopback origin as trustworthy and keeps the cookies anyway, so most of the
# browser suite survives the production value -- but not all of it, and the
# exception was measured rather than guessed: with these two lines removed,
# ``test_the_editor_and_its_endpoint_are_staff_only`` fails, because the
# request Playwright makes outside the page sends no secure cookie and the
# endpoint answers with a CSRF failure instead of the staff refusal the test is
# about. Turned off here rather than in ``common_settings``, so that the value
# a deployment inherits is the safe one;
# ``kasvimuseo/tests/test_settings_cookie_security.py`` asserts the production
# value by reading ``common_settings`` directly and switching it back on for
# the tests that need it.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# The default hasher is deliberately slow; tests create users constantly.
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
# Tests that need real image files override this with a temporary directory;
# see the ``media_root`` fixture in ``kasvimuseo/tests/conftest.py``. The
# variable is for the browser tests, which run the server in one container and
# seed it from another, so the two need somewhere both of them can see -- these
# settings serve the server there as well as the suite (issue 017).
MEDIA_ROOT = os.environ.get('KASVIMUSEO_MEDIA_ROOT',
                            '/tmp/kasvimuseo-test-media')

# Don't try to mail admins about exceptions raised inside tests.
LOGGING = dict(LOGGING, loggers={})  # noqa: F405
