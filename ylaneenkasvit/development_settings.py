# -*- encoding: utf-8 -*-
"""Settings for the development server (issue 067).

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
screen says why (issue 067). These settings are tracked, so they arrive with a
``git pull`` and are reviewable in a diff.

``local_settings.py`` still exists and is still applied, last and on top of
everything here, but only what is genuinely particular to one machine belongs
in it now.
"""

import os

from .common_settings import *  # noqa

# ``dev/kasvimuseo`` passes a development key, and the image sets
# ``KASVIMUSEO_DEBUG``; the production key is in the Ansible Vault and is in no
# tracked file (issue 025), so this is read rather than written out.
SECRET_KEY = secret_from_env('KASVIMUSEO_SECRET_KEY')  # noqa: F405

# A development server is reached under whatever name its developer published
# it -- localhost, a container IP, a tailnet name -- and it is on a machine
# that is not on the internet. Production's list comes from the environment
# (issue 026) and is never this.
ALLOWED_HOSTS = ['*']

# ``django-extensions`` is in ``requirements/dev.txt`` alone since upgrade plan
# Stage 0, so a production install has neither the package nor this entry. It
# is what ``runserver_plus`` and ``shell_plus`` come from
# (``dev/kasvimuseo app manage runserver_plus``), and ``runserver_plus`` is what
# replaced ``django-pserver`` (issue 033).
INSTALLED_APPS += ('django_extensions',)  # noqa: F405

# ``common_settings`` marks both cookies ``Secure``, because production is
# TLS-only (issue 059). This server is plain HTTP, and a browser keeps a secure
# cookie from a plain-HTTP response only when the origin is loopback, which it
# treats as trustworthy anyway. ``http://localhost:8000`` is therefore the case
# that would *hide* this; the case that does not is the one this project
# actually has, a browser on another machine reaching the server by name (issue
# 044). Measured with these two lines removed: such a client keeps no session
# cookie, so the admin login form comes back instead of the dashboard however
# right the password is, with nothing on screen to say why -- which is issue
# 067, reported after the same two lines sat unreachable in a template for two
# weeks. Relaxed here, in the file that already knows it is development, rather
# than by weakening the value production inherits.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# The defaults match dev/kasvimuseo, which passes these through to the app
# container as environment variables.
#
# A new dictionary rather than ``DATABASES['default'].update(...)``, which is
# how ``ylaneenkasvit_settings`` and ``test_settings`` do it. Those are only
# ever the settings in force, and this module is also *imported* -- by
# ``kasvimuseo/tests/test_settings_cookie_security.py``, which is the test 067
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

# Serve photos from this server, and fall back to the production media host for
# the ones this machine does not have -- so a fresh clone shows every photo
# without downloading 260 MB, while a photo uploaded here is the local file
# rather than a 404 from a host that never saw it (issue 048).
#
# Two views still open the image files to read their dimensions, which no URL
# can satisfy, so for those:
#
#   $ dev/kasvimuseo media fetch
#
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'
MEDIA_FALLBACK_URL = 'https://media.kasvit.ambitone.com/'

GRAPPELLI_ADMIN_TITLE = u'Yläneen perinnekasvit (kehitys)'

# Whatever is particular to this one machine, applied last, exactly as
# ``ylaneenkasvit_settings`` does it in production: a ``modify(globals())``
# function in an untracked ``ylaneenkasvit/local_settings.py``. Nothing needs
# one -- ``dev/kasvimuseo`` no longer writes it, and everything it used to hold
# is above.
try:
    from local_settings import *  # noqa
    modify(globals())  # noqa: F405
except ImportError:
    pass
