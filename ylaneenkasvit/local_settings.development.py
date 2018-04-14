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

# Load media from production. To use this, Django needs to access media files
# locally to find out image dimensions. Mount the production media directory
# using:
#
#   $ sshfs -o akaihola@kasvit.ambitone.com:/www/ylaneenkasvit/media media
#
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '//media.kasvit.ambitone.com/'
#MEDIA_URL = '/media/'
