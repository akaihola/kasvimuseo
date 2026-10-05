# -*- encoding: utf-8 -*-
"""Settings for operators who configure a site through environment variables."""

from .common_settings import *  # noqa

SITE_ROOT = PROJECT_ROOT  # noqa: F405
DATABASES['default'].update({  # noqa: F405
    'NAME': secret_from_env('KASVIMUSEO_DB_NAME'),  # noqa: F405
    'USER': secret_from_env('KASVIMUSEO_DB_USER'),  # noqa: F405
    'PASSWORD': secret_from_env('KASVIMUSEO_DB_PASSWORD'),  # noqa: F405
    'HOST': os.environ.get('KASVIMUSEO_DB_HOST', '/var/run/postgresql'),  # noqa: F405
    'PORT': os.environ.get('KASVIMUSEO_DB_PORT', ''),  # noqa: F405
})
SECRET_KEY = secret_from_env('KASVIMUSEO_SECRET_KEY')  # noqa: F405
ALLOWED_HOSTS = hosts_from_env('KASVIMUSEO_ALLOWED_HOSTS')  # noqa: F405
STATIC_URL = os.environ.get('KASVIMUSEO_STATIC_URL', '/static/')  # noqa: F405
MEDIA_URL = os.environ.get('KASVIMUSEO_MEDIA_URL', '/media/')  # noqa: F405
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')  # noqa: F405
GRAPPELLI_ADMIN_TITLE = os.environ.get('KASVIMUSEO_SITE_TITLE', 'Kasvimuseo')  # noqa: F405
ADMINS = ((os.environ.get('KASVIMUSEO_ADMIN_NAME', 'Admin'),  # noqa: F405
           os.environ['KASVIMUSEO_ADMIN_EMAIL']),) if os.environ.get(  # noqa: F405
               'KASVIMUSEO_ADMIN_EMAIL') else ()
MANAGERS = ADMINS
