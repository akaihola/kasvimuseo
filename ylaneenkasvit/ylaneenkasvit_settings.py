# -*- encoding: utf-8 -*-

from .common_settings import *

SITE_ROOT = '/www/ylaneenkasvit'

ADMINS = (('Antti Kaihola', 'akaihol+ylaneenkasvit@ambitone.com'),)
MANAGERS = ADMINS

DATABASES['default'].update({
    'NAME': 'ylaneenkasvit',
    'USER': 'ylaneenkasvit',
    'PASSWORD': '5tsovi25'})

SECRET_KEY = ';)bi?F@=#NZO!"kXr`ls7Z,s-,$oPQ"b1ohGZ6O$(!l(uQCn-U\'/HP^d4onE~d+'

STATIC_URL = 'http://static.kasvit.ambitone.com/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'

GRAPPELLI_ADMIN_TITLE = u'Yläneen perinnekasvit'
MEDIA_URL = 'http://media.kasvit.ambitone.com'
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

try:
    from ylaneenkasvit.local_settings import *
    modify(globals())
except ImportError:
    pass
