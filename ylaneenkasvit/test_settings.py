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

# The default hasher is deliberately slow; tests create users constantly.
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'
MEDIA_URL = '/media/'
# Tests that need real image files override this with a temporary directory;
# see the ``media_root`` fixture in ``kasvimuseo/tests/conftest.py``.
MEDIA_ROOT = '/tmp/kasvimuseo-test-media'

# Don't try to mail admins about exceptions raised inside tests.
LOGGING = dict(LOGGING, loggers={})  # noqa: F405
