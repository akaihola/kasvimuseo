"""Check the environment interface for independently configured installations."""

import copy
import runpy

import pytest
from django.core.exceptions import ImproperlyConfigured

from ylaneenkasvit import common_settings


@pytest.fixture
def site_environment(monkeypatch):
    monkeypatch.setattr(common_settings, 'DATABASES', copy.deepcopy(common_settings.DATABASES))
    for name, value in {
        'DB_NAME': 'sample_catalogue',
        'DB_USER': 'sample_operator',
        'DB_PASSWORD': 'test-password',
        'SECRET_KEY': 'test-key',
        'ALLOWED_HOSTS': 'plants.example.invalid',
    }.items():
        monkeypatch.setenv('KASVIMUSEO_' + name, value)
    for name in ['STATIC_URL', 'MEDIA_URL', 'ADMIN_EMAIL', 'ADMIN_NAME', 'SITE_TITLE']:
        monkeypatch.delenv('KASVIMUSEO_' + name, raising=False)


def test_site_settings_use_supplied_database_and_local_assets(site_environment):
    settings = runpy.run_module('ylaneenkasvit.ylaneenkasvit_settings')
    assert settings['DATABASES']['default']['NAME'] == 'sample_catalogue'
    assert settings['DATABASES']['default']['USER'] == 'sample_operator'
    assert settings['STATIC_URL'] == '/static/'
    assert settings['MEDIA_URL'] == '/media/'
    assert settings['ADMINS'] == ()
    assert settings['ALLOWED_HOSTS'] == ['plants.example.invalid']


@pytest.mark.parametrize('name', ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'SECRET_KEY', 'ALLOWED_HOSTS'])
def test_site_settings_require_configuration(site_environment, monkeypatch, name):
    monkeypatch.delenv('KASVIMUSEO_' + name)
    with pytest.raises(ImproperlyConfigured, match='KASVIMUSEO_' + name):
        runpy.run_module('ylaneenkasvit.ylaneenkasvit_settings')


def test_site_settings_accept_asset_and_contact_configuration(site_environment, monkeypatch):
    monkeypatch.setenv('KASVIMUSEO_MEDIA_URL', 'https://media.example.invalid/')
    monkeypatch.setenv('KASVIMUSEO_STATIC_URL', 'https://static.example.invalid/')
    monkeypatch.setenv('KASVIMUSEO_ADMIN_EMAIL', 'operator@example.invalid')
    monkeypatch.setenv('KASVIMUSEO_ADMIN_NAME', 'Operator')
    settings = runpy.run_module('ylaneenkasvit.ylaneenkasvit_settings')
    assert settings['MEDIA_URL'] == 'https://media.example.invalid/'
    assert settings['STATIC_URL'] == 'https://static.example.invalid/'
    assert settings['ADMINS'] == (('Operator', 'operator@example.invalid'),)
