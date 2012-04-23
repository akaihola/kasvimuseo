import os


DEBUG = True
TEMPLATE_DEBUG = DEBUG
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'HOST': '/var/run/postgresql'}}

def modify(settings):
    db = settings['DATABASES']['default']
    db['HOST'] = os.path.join(os.path.dirname(__file__), '..', 'db')
    db['NAME'] = 'ylaneenkasvit'

    #settings['INSTALLED_APPS'] += 'pserver', 'django_extensions',


PROJECT_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
#ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'
#MEDIA_URL = 'http://media.kasvit.local'
#MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
