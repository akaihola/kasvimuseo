import os


def modify(settings):
    settings['DEBUG'] = True
    settings['TEMPLATE_DEBUG'] = True

    db = settings['DATABASES']['default']
    db['HOST'] = '/var/run/postgresql'
    db['NAME'] = 'ylaneenkasvit'
    db['PORT'] = 5432

    #settings['INSTALLED_APPS'] += 'pserver', 'django_extensions',


    settings['PROJECT_ROOT'] = os.path.realpath(
        os.path.join(os.path.dirname(__file__), ''))
    settings['STATIC_ROOT'] = os.path.join(settings['PROJECT_ROOT'], 'static')
    settings['STATIC_URL'] = '/static/'

    # Load media from production. To use this, Django needs to access media files
    # locally to find out image dimensions. Mount the production media directory
    # using:
    #
    #   $ sshfs -o akaihola@kasvit.ambitone.com:/www/ylaneenkasvit/media media
    #
    settings['MEDIA_ROOT'] = os.path.join(settings['PROJECT_ROOT'], 'media')
    settings['MEDIA_URL'] = '//media.kasvit.ambitone.com/'
    #MEDIA_URL = '/media/'
