# -*- encoding: utf-8 -*-
"""Settings for the development server (issue 069).

The site settings module ``dev/kasvimuseo`` runs the application on, and the
counterpart of ``ylaneenkasvit_settings`` for production and ``test_settings``
for the suite. Built on ``common_settings`` for the same reason
``test_settings`` is: nothing here should depend on the untracked
``local_settings.py`` of whoever runs it.

Everything below used to be in ``local_settings.development.py``, which is a
*template*: ``dev/kasvimuseo`` copies it to ``local_settings.py`` when a
checkout has none, and never touches it again. So a setting added to the
template reached nobody who had already cloned, and there was no way to tell
from the running application which of them a copy was missing. Twice that was
found from the outside instead -- photos loaded from the production media host
(issue 048), and then a development server issuing ``Secure`` cookies over
plain HTTP, where a correct password returns the login form and nothing on
screen says why (issue 069). These settings are tracked, so they arrive with a
``git pull`` and are reviewable in a diff.

``local_settings.py`` still exists and is still applied, last and on top of
everything here, but only what is genuinely particular to one machine belongs
in it now.
"""

import os

from .common_settings import *  # noqa

SECRET_KEY = secret_from_env('KASVIMUSEO_SECRET_KEY')  # noqa: F405

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += ('django_extensions',)  # noqa: F405

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# The defaults match dev/kasvimuseo, which passes these through to the app
# container as environment variables.
#
# A new dictionary rather than ``DATABASES['default'].update(...)``, which is
# how ``ylaneenkasvit_settings`` and ``test_settings`` do it. Those are only
# ever the settings in force, and this module is also *imported* -- by
# ``kasvimuseo/tests/test_settings_cookie_security.py``, which is the test 069
# added to look at what the development server actually loads. ``import *``
# binds ``common_settings``'s own dictionary, not a copy, so updating it in
# place would repoint the running suite's database at the development one:
# measured, and it is 45 errors and 73 failures of "relation does not exist".
DATABASES = {'default': dict(
    DATABASES['default'],  # noqa: F405
    HOST=os.environ.get('KASVIMUSEO_DB_HOST', '/var/run/postgresql'),
    # A string, as in ``test_settings``: psycopg2 is handed ``str(port)``
    # whatever this is.
    PORT=os.environ.get('KASVIMUSEO_DB_PORT', '5432'),
    NAME=os.environ.get('KASVIMUSEO_DB_NAME', 'ylaneenkasvit'),
    USER=os.environ.get('KASVIMUSEO_DB_USER', 'ylaneenkasvit'),
    # The local cluster trusts local connections, so this authenticates
    # nothing; it is read rather than defaulted for the reason 025 gives.
    PASSWORD=os.environ.get('KASVIMUSEO_DB_PASSWORD', ''),
)}

# The repository root, one level up from this package: static/ and media/ live
# there, and that is where collectstatic writes.
PROJECT_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

# Missing local photos return 404 unless the developer supplies a fallback.
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'
MEDIA_FALLBACK_URL = os.environ.get('KASVIMUSEO_MEDIA_FALLBACK_URL', '')

GRAPPELLI_ADMIN_TITLE = u'Yläneen perinnekasvit (kehitys)'

try:
    from local_settings import *  # noqa
    modify(globals())  # noqa: F405
except ImportError:
    pass
