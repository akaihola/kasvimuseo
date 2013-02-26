# -*- encoding: utf-8 -*-

import os

PROJECT_ROOT = '/www/ylaneenkasvit'
here = lambda *args: os.path.join(os.path.dirname(__file__), *args)

# specify SITE_ROOT in site specific settings

# specify ADMINS and MANAGERS in site specific settings
ADMINS = (('Admin', 'admin@invalid'),)
MANAGERS = ADMINS

# specify database NAME, USER and PASSWORD in site specific settings
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'HOST': '/var/run/postgresql'}}

LANGUAGE_CODE = 'fi'
TIME_ZONE = 'Europe/Helsinki'
USE_TZ = True

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
    'jqm',
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

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# specify in site specific settings:
#STATIC_URL = 'http://STATIC_URL/'
#ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'
#GRAPPELLI_ADMIN_TITLE = u'GRAPPELLI_ADMIN_TITLE'
#MEDIA_URL = 'http://MEDIA_URL'
#MEDIA_ROOT = os.path.join(SITE_ROOT, 'MEDIA_ROOT')

GRAPPELLI_INDEX_DASHBOARD = 'ylaneenkasvit.dashboard.CustomIndexDashboard'
DATE_FORMAT = 'Y-m-d'

SOUTH_MIGRATION_MODULES = {
    'photologue': 'ylaneenkasvit.external_migrations.photologue',
}

DEBUG = False
TEMPLATE_DEBUG = True
