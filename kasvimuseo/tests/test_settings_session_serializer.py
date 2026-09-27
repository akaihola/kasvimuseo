# -*- coding: utf-8 -*-
"""These tests let maintainers check that stored sessions contain JSON.

Issue 057 records why the project requires JSON serialization.
"""

from __future__ import unicode_literals

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core import signing
from django.urls import reverse
from django.test.utils import override_settings

PASSWORD = 'salasana'

SESSION_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


@pytest.fixture
def user(db):
    return User.objects.create_user('puutarhuri', 'p@invalid', PASSWORD)


def stored_payload(client):
    """Read the stored session with JSON, independent of the configured serializer."""
    row = Session.objects.get(session_key=client.session.session_key)
    return signing.loads(row.session_data, salt=client.session.key_salt,
                         serializer=signing.JSONSerializer)


def test_the_configured_serializer_is_the_json_one():
    assert settings.SESSION_SERIALIZER == (
        'django.contrib.sessions.serializers.JSONSerializer')


def test_a_logged_in_session_is_stored_as_json(client, user):
    """The regression test: pickle output is not JSON, so this fails without
    the setting."""
    assert client.login(username=user.username, password=PASSWORD)

    payload = stored_payload(client)

    # A string since Django 1.8, which serializes the pk field's value.
    assert payload['_auth_user_id'] == str(user.pk)
    assert payload['_auth_user_backend'] == (
        'django.contrib.auth.backends.ModelBackend')


def test_messages_round_trip_through_a_json_session(admin_client):
    """The one framework that puts something structured in the session.

    ``MESSAGE_STORAGE`` resolves to ``FallbackStorage`` here, so messages
    normally go in a cookie and only reach the session when they outgrow it.
    That fallback is forced on here, because it is the branch JSON could break
    -- and it does not: Django 1.5's ``SessionStorage`` stores
    ``MessageEncoder``'s JSON string, which is a string like any other.

    ``override_settings`` is used as a context manager rather than as a
    decorator: its ``wraps`` hides the signature, and pytest then has no
    ``admin_client`` argument to fill in.
    """
    with override_settings(MESSAGE_STORAGE=SESSION_STORAGE):
        response = admin_client.post(
            reverse('admin:kasvimuseo_species_add'),
            {'name_fi': 'kevätesikko', 'genus': 'Primula',
             'species': 'veris', 'type': '2',
             'observation_set-TOTAL_FORMS': '0',
             'observation_set-INITIAL_FORMS': '0',
             'observation_set-MAX_NUM_FORMS': ''})

        assert response.status_code == 302, 'the add form did not save'
        payload = stored_payload(admin_client)
        assert '_messages' in payload

        body = admin_client.get(response['Location']).content.decode('utf-8')
    assert 'kevätesikko' in body
