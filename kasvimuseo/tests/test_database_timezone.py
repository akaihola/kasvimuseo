"""These tests check PostgreSQL timestamp decoding for runtime maintainers."""

from datetime import datetime, timedelta, timezone

import pytest
from django.conf import settings
from django.db import connection
from django.utils.timezone import is_aware


@pytest.mark.django_db
def test_postgresql_returns_aware_utc_timestamp():
    """The driver must preserve an instant when Django decodes its timestamp."""
    assert settings.USE_TZ is True
    assert settings.TIME_ZONE == 'Europe/Helsinki'
    instant = datetime(2020, 6, 1, 12, 30,
                       tzinfo=timezone(timedelta(hours=3)))

    with connection.cursor() as cursor:
        cursor.execute('SELECT %s::timestamptz', [instant])
        result = cursor.fetchone()[0]

    assert is_aware(result)
    assert result.utcoffset() == timedelta(0)
    assert result == instant
