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
)

ROOT_URLCONF = 'urls'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
