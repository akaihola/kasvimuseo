import os


def modify(settings):
    settings['DEBUG'] = True
    settings['TEMPLATE_DEBUG'] = True

    # Development only, which is why it is here and not in common_settings:
    # `django-extensions` is in `requirements/dev.txt` alone since upgrade plan
    # Stage 0, so a production install has neither the package nor this entry.
    # It is what `runserver_plus` and `shell_plus` come from
    # (`dev/kasvimuseo app manage runserver_plus`), and `runserver_plus` is
    # what replaced `django-pserver` (issue 033).
    settings['INSTALLED_APPS'] += ('django_extensions',)

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
