import os


def modify(settings):
    settings['DEBUG'] = True
    settings['TEMPLATE_DEBUG'] = True

    # The defaults match dev/kasvimuseo, which passes these through to the app
    # container as environment variables.
    db = settings['DATABASES']['default']
    db['HOST'] = os.environ.get('KASVIMUSEO_DB_HOST', '/var/run/postgresql')
    db['PORT'] = int(os.environ.get('KASVIMUSEO_DB_PORT', '5432'))
    db['NAME'] = os.environ.get('KASVIMUSEO_DB_NAME', 'ylaneenkasvit')
    db['USER'] = os.environ.get('KASVIMUSEO_DB_USER', 'ylaneenkasvit')

    #settings['INSTALLED_APPS'] += 'pserver', 'django_extensions',

    # The repository root, one level up from this package: static/ and media/
    # live there, and that is where collectstatic writes.
    settings['PROJECT_ROOT'] = os.path.realpath(
        os.path.join(os.path.dirname(__file__), '..'))
    settings['STATIC_ROOT'] = os.path.join(settings['PROJECT_ROOT'], 'static')
    settings['STATIC_URL'] = '/static/'

    # Load media from production. Django still needs the image files locally to
    # find out their dimensions, so get them with:
    #
    #   $ dev/kasvimuseo media fetch
    #
    settings['MEDIA_ROOT'] = os.path.join(settings['PROJECT_ROOT'], 'media')
    settings['MEDIA_URL'] = '//media.kasvit.ambitone.com/'
    #MEDIA_URL = '/media/'

    # The dev server is reached under whatever name the developer published it.
    settings['ALLOWED_HOSTS'] = ['*']
