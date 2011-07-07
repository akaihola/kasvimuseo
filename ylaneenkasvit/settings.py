# -*- encoding: utf-8 -*-

import os

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'ylaneenkasvit',
    'HOST': 'localhost',
    'USER': 'ylaneenkasvit',
    'PASSWORD': '5tsovi25'}}

LANGUAGE_CODE = 'fi'

INSTALLED_APPS = (
    'kasvimuseo',

    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'gunicorn',
    'south',

    'indexer',
    'paging',
    'sentry',
    'sentry.client',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    #'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATE_DIRS = os.path.join(PROJECT_ROOT, 'templates'),

ROOT_URLCONF = 'ylaneenkasvit.urls'

STATIC_URL = '/media/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'

GRAPPELLI_ADMIN_TITLE = u'Yläneen perinnekasvit'
GRAPPELLI_INDEX_DASHBOARD = 'ylaneenkasvit.dashboard.CustomIndexDashboard'
DATE_FORMAT = 'Y-m-d'

DEBUG = False
TEMPLATE_DEBUG = True

try:
    from ylaneenkasvit.local_settings import *
    modify(globals())
except ImportError:
    pass
