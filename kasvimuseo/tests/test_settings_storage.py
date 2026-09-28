"""These checks protect media and static storage settings during runtime upgrades."""

from django.core.files.storage import FileSystemStorage, storages
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.test import override_settings

from ylaneenkasvit import common_settings


def test_storage_backends_keep_filesystem_behavior(tmp_path):
    with override_settings(STORAGES=common_settings.STORAGES,
                           MEDIA_ROOT=str(tmp_path / 'media'),
                           STATIC_ROOT=str(tmp_path / 'static')):
        assert isinstance(storages['default'], FileSystemStorage)
        assert storages['default'].location == str(tmp_path / 'media')
        assert isinstance(storages['staticfiles'], StaticFilesStorage)
        assert storages['staticfiles'].location == str(tmp_path / 'static')
