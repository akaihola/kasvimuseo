# -*- encoding: utf-8 -*-

from .common_settings import *

SITE_ROOT = '/www/kajalankasvit'

ADMINS = (('Antti Kaihola', 'akaihol+kajalankasvit@ambitone.com'),)
MANAGERS = ADMINS

DATABASES['default'].update({
    'NAME': 'kajalankasvit',
    'USER': 'kajalankasvit',
    'PASSWORD': '6dofoso11'})

STATIC_URL = 'http://static.kajalankasvit.ambitone.com/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'

GRAPPELLI_ADMIN_TITLE = u'Kajalan kasvimaat'
MEDIA_URL = 'http://media.kajalankasvit.ambitone.com/'
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

try:
    from ylaneenkasvit.local_settings import *
    modify(globals())
except ImportError:
    pass
