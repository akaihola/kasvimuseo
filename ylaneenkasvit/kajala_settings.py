# -*- encoding: utf-8 -*-

from .common_settings import *

SITE_ROOT = '/www/kajalankasvit'

ADMINS = (('Antti Kaihola', 'akaihol+kajalankasvit@ambitone.com'),)
MANAGERS = ADMINS

# From the environment, not from this file, and with no default: the password
# that used to stand here is in the history and is disclosed until it is
# rotated (issue 025).
DATABASES['default'].update({
    'NAME': 'kajalankasvit',
    'USER': 'kajalankasvit',
    'PASSWORD': secret_from_env('KASVIMUSEO_DB_PASSWORD')})

# As in ylaneenkasvit_settings: from the environment, no default (issue 026).
ALLOWED_HOSTS = hosts_from_env('KASVIMUSEO_ALLOWED_HOSTS')

STATIC_URL = '//static.kajalankasvit.ambitone.com/'

GRAPPELLI_ADMIN_TITLE = u'Kajalan kasvimaat'
MEDIA_URL = '//media.kajalankasvit.ambitone.com/'
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

try:
    from local_settings import *
    modify(globals())
except ImportError:
    pass
