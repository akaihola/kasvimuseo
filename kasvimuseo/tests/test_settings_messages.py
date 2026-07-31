# -*- coding: utf-8 -*-
"""Tests for the messages framework being configured whole (issue 023).

The context processor and the middleware were both in place while the app was
not. Django 1.5 tolerates that; from 1.7 the admin's system checks do not, and
the admin is this application. The app entry is now there, and this pins all
three halves together so that removing one is a deliberate act rather than the
half-configuration this issue was about.

The default storage is ``FallbackStorage`` -- cookie first, session second --
so the app owns no table and needs no migration. That is asserted too, since it
is the reason adding the app changed nothing about the database.
"""

from __future__ import unicode_literals

from django.conf import settings
from django.db.models import get_app, get_models


def test_messages_app_is_installed():
    assert 'django.contrib.messages' in settings.INSTALLED_APPS


def test_messages_middleware_and_context_processor_are_configured():
    assert ('django.contrib.messages.middleware.MessageMiddleware'
            in settings.MIDDLEWARE_CLASSES)
    assert ('django.contrib.messages.context_processors.messages'
            in settings.TEMPLATE_CONTEXT_PROCESSORS)


def test_the_messages_app_brings_no_models():
    """Nothing to migrate: the storage is cookies and the session."""
    assert settings.MESSAGE_STORAGE == (
        'django.contrib.messages.storage.fallback.FallbackStorage')
    assert get_models(get_app('messages')) == []
