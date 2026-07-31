# -*- encoding: utf-8 -*-

from .common_settings import *

SITE_ROOT = '/www/ylaneenkasvit'

ADMINS = (('Antti Kaihola', 'akaihol+ylaneenkasvit@ambitone.com'),)
MANAGERS = ADMINS

# The password and the secret key are read from the environment and are not in
# this file: they were committed here in plain text, and are still in the
# history, so both are disclosed until the maintainer rotates them (issue 025).
# ``secret_from_env`` has no default on purpose -- see common_settings.
DATABASES['default'].update({
    'NAME': 'ylaneenkasvit',
    'USER': 'ylaneenkasvit',
    'PASSWORD': secret_from_env('KASVIMUSEO_DB_PASSWORD')})

SECRET_KEY = secret_from_env('KASVIMUSEO_SECRET_KEY')

# The names this site answers to, from the environment and with no default
# (issue 026). Ansible writes them into uwsgi.ini from ``kasvimuseo_allowed_hosts``
# in ``ansible/vars/main.yml``; unlike the secrets these are not vaulted, since a
# host name is not a secret and the deployment should be reproducible from what
# is tracked here.
ALLOWED_HOSTS = hosts_from_env('KASVIMUSEO_ALLOWED_HOSTS')

STATIC_URL = '//static.kasvit.ambitone.com/'

GRAPPELLI_ADMIN_TITLE = u'Yläneen perinnekasvit'
MEDIA_URL = '//media.kasvit.ambitone.com/'
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

try:
    from local_settings import *
    modify(globals())
except ImportError:
    pass
