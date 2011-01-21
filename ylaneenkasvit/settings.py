import os

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'ylaneenkasvit.sqlite'}}

LANGUAGE_CODE = 'fi'

INSTALLED_APPS = (
    'kasvimuseo',

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

TEMPLATE_DIRS = os.path.join(PROJECT_ROOT, 'templates'),

ROOT_URLCONF = 'ylaneenkasvit.urls'

ADMIN_MEDIA_PREFIX = '/admin/media/'

DEBUG = False
TEMPLATE_DEBUG = True
