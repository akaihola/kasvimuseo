# -*- encoding: utf-8 -*-

import os

PROJECT_ROOT = '/www/ylaneenkasvit'
here = lambda *args: os.path.join(os.path.dirname(__file__), *args)

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'ylaneenkasvit',
    'HOST': 'localhost',
    'USER': 'ylaneenkasvit',
    'PASSWORD': '5tsovi25'}}

LANGUAGE_CODE = 'fi'

INSTALLED_APPS = (
    'ylaneenkasvit',  # for fixtures
    'kasvimuseo',

    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'gunicorn',
    'south',

    'indexer',
    'paging',
    'photologue',

    'sentry',
    'sentry.client',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATE_DIRS = (here('templates'),
                 here('..', 'lib', 'python2.7', 'site-packages',
                      'photologue', 'templates'))

ROOT_URLCONF = 'ylaneenkasvit.urls'

STATIC_URL = 'http://static.kasvit.ambitone.com/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'

GRAPPELLI_ADMIN_TITLE = u'Yläneen perinnekasvit'
MEDIA_URL = 'http://media.kasvit.ambitone.com'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
GRAPPELLI_INDEX_DASHBOARD = 'ylaneenkasvit.dashboard.CustomIndexDashboard'
DATE_FORMAT = 'Y-m-d'

SOUTH_MIGRATION_MODULES = {
    'photologue': 'ylaneenkasvit.external_migrations.photologue',
}

DEBUG = False
TEMPLATE_DEBUG = True

try:
    from ylaneenkasvit.local_settings import *
    modify(globals())
except ImportError:
    pass
