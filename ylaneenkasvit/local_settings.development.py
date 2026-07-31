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

    # The repository root, one level up from this package: static/ and media/
    # live there, and that is where collectstatic writes.
    settings['PROJECT_ROOT'] = os.path.realpath(
        os.path.join(os.path.dirname(__file__), '..'))
    settings['STATIC_ROOT'] = os.path.join(settings['PROJECT_ROOT'], 'static')
    settings['STATIC_URL'] = '/static/'

    # Serve photos from this server, and fall back to the production media
    # host for the ones this machine does not have -- so a fresh clone shows
    # every photo without downloading 260 MB, while a photo uploaded here is
    # the local file rather than a 404 from a host that never saw it.
    #
    # Two views still open the image files to read their dimensions, which no
    # URL can satisfy, so for those:
    #
    #   $ dev/kasvimuseo media fetch
    #
    settings['MEDIA_ROOT'] = os.path.join(settings['PROJECT_ROOT'], 'media')
    settings['MEDIA_URL'] = '/media/'
    settings['MEDIA_FALLBACK_URL'] = 'https://media.kasvit.ambitone.com/'

    # The dev server is reached under whatever name the developer published it.
    settings['ALLOWED_HOSTS'] = ['*']
