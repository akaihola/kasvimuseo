# -*- coding: utf-8 -*-
"""Tests for an unhandled exception being written down somewhere (issue 065),
and for it being written down *only* there (issue 066).

Django's stock ``LOGGING`` block sends a 500's traceback to
``AdminEmailHandler`` and nowhere else. Nothing installs an MTA on the server
and no settings module sets ``EMAIL_*``, so that handler mails ``localhost:25``
and ``mail_admins(..., fail_silently=True)`` swallows the refusal. While
production runs with ``DEBUG`` on (issue 051) this is invisible, because
Django's own ``DEFAULT_LOGGING`` puts a ``RequireDebugTrue``-filtered console
handler on the ``django`` logger; the day 051 is acted on, the traceback stops
existing.

That mail handler is gone now. 065 added the stream handler, which made the
mail a second copy of something already written down; 066 asked whether the
second copy was worth having and the maintainer ruled that it was not --
``uwsgi.error.log`` is enough. So two of the tests below pin an absence rather
than a presence, which is the same job in reverse: Django's stock block has an
``AdminEmailHandler`` in it, and a copy-paste would put one back silently.

Django 1.6 (upgrade plan Stage 3) added a second logger with the same defect,
``django.security``, so the same thing holds for a ``Host`` header that
``ALLOWED_HOSTS`` refuses.

The behavioural tests are the ones that matter: each configures logging exactly
as ``common_settings`` describes it -- with the console handler's stream swapped
for a buffer, which is the only thing it changes -- provokes the thing Django
logs, and reads what was written. On the configuration this issue describes the
buffer stays empty.

``common_settings`` is imported directly rather than read off ``settings``,
because ``test_settings`` deliberately gives every logger here an empty handler
list: the suite breaks requests on purpose and pytest already reports each one.
"""

from __future__ import unicode_literals

import copy
import logging
import logging.config

import pytest
from django.conf import settings
from django.conf.urls import patterns, url
from django.core.urlresolvers import clear_url_caches
from django.test.utils import override_settings
from django.utils.six import StringIO

from ylaneenkasvit import common_settings

LOGGING = common_settings.LOGGING

WRITING_HANDLERS = ('logging.StreamHandler', 'logging.FileHandler',
                    'logging.handlers.WatchedFileHandler',
                    'logging.handlers.RotatingFileHandler')


def crash(request):
    raise ZeroDivisionError('deliberate, from test_settings_logging')


urlpatterns = patterns('', url(r'^crash/$', crash))


def handlers_reaching(logger_name):
    """The handler names a record on ``logger_name`` would be given.

    The logger's own handlers, plus ``root``'s when it propagates -- which is
    the whole of what ``LOGGING`` says about where a record ends up.
    """
    logger = LOGGING['loggers'][logger_name]
    names = list(logger['handlers'])
    if logger.get('propagate', True):
        names += LOGGING.get('root', {}).get('handlers', [])
    return names


@pytest.mark.parametrize('logger_name', ['django.request', 'django.security'])
def test_an_error_reaches_a_handler_that_writes_somewhere(logger_name):
    """The regression test in configuration form: each of these loggers has to
    have a handler that writes, not only one that mails.

    ``django.security`` is Django 1.6's addition (upgrade plan Stage 3) and
    arrived with the same defect: ``DEFAULT_LOGGING`` gives it ``mail_admins``
    alone, so a ``SuspiciousOperation`` went the same nowhere a 500 did.
    """
    classes = [LOGGING['handlers'][name]['class']
               for name in handlers_reaching(logger_name)]

    assert [c for c in classes if c in WRITING_HANDLERS], (
        '%s has no handler that writes anywhere: %r' % (logger_name, classes))


def test_the_console_handler_is_not_filtered_by_debug():
    """``DEFAULT_LOGGING``'s console handler carries ``RequireDebugTrue``,
    which is exactly why turning ``DEBUG`` off loses the traceback. This one
    must not, or the fix is only a fix in development."""
    assert LOGGING['handlers']['console'].get('filters', []) == []


def test_nothing_here_mails_an_error():
    """The reverse of what this file asserted until issue 066 was ruled on.

    It used to pin that ``mail_admins`` was still configured, so that removing
    it would be a decision rather than a tidy-up. The decision was taken -- the
    maintainer ruled that ``uwsgi.error.log`` is enough -- so the assertion is
    turned around and pins the absence for the same reason: Django's stock
    block has an ``AdminEmailHandler`` and a copy-paste of it would put one
    back silently.

    Every handler is checked rather than only the two loggers', because a
    mailing handler defined and left unreferenced is the same defect one edit
    later.
    """
    mailing = [name for name, handler in LOGGING['handlers'].items()
               if 'EmailHandler' in handler.get('class', '')]

    assert mailing == [], (
        'issue 066 deleted the mail path deliberately; these are back: %r'
        % (mailing,))


def test_no_settings_module_points_the_mail_anywhere():
    """The other half of 066's ruling: there is no relay either.

    Django's defaults are ``localhost:25`` over SMTP, which nothing on the
    production host listens on -- that is what made the deleted handler inert
    rather than merely unused. Asserted so that a later change which points the
    mail somewhere real has to notice that nothing is left to send it.
    """
    assert settings.EMAIL_HOST == 'localhost'
    assert settings.EMAIL_PORT == 25


@pytest.fixture
def request_log(request):
    """Logging configured as ``common_settings`` has it, writing to a buffer.

    Everything is the real configuration except the console handler's stream,
    which is where this fixture reads. The suite's own configuration is put
    back afterwards, so a test that follows this one is as quiet as it was.
    """
    buffer = StringIO()
    config = copy.deepcopy(LOGGING)
    console = config['handlers'].get('console')
    if console is not None:
        console['stream'] = buffer
    # Deliberately not an error when there is none: on the configuration this
    # issue describes there is nothing to point at a buffer, and the test
    # should fail by finding the buffer empty rather than by raising here.
    logging.config.dictConfig(config)

    def restore():
        logging.config.dictConfig(settings.LOGGING)

    request.addfinalizer(restore)
    return buffer


def test_an_unhandled_exception_is_written_to_the_stream(client, request_log):
    """With ``DEBUG`` off, the traceback of a 500 is on the handler's stream.

    ``DEBUG`` is off here because Django's test runner forces it off, which is
    the state issue 051 will leave production in. The test client re-raises the
    exception after the handler has dealt with it, so the ``raises`` is about
    the client rather than about the logging.
    """
    assert not settings.DEBUG

    clear_url_caches()
    try:
        with override_settings(ROOT_URLCONF=__name__):
            with pytest.raises(ZeroDivisionError):
                client.get('/crash/')
    finally:
        clear_url_caches()

    written = request_log.getvalue()

    assert 'Internal Server Error: /crash/' in written
    assert 'ZeroDivisionError' in written
    assert 'deliberate, from test_settings_logging' in written
    assert 'in crash' in written, 'the traceback itself is not there: %r' % (
        written,)


def test_a_rejected_host_header_is_written_to_the_stream(client, request_log):
    """The same for ``django.security``, through the one path this project can
    reach: a ``Host`` header that ``ALLOWED_HOSTS`` (issue 026) refuses.

    Django 1.6 answers 400 and logs it to ``django.security.DisallowedHost``.
    ``ALLOWED_HOSTS`` is overridden because ``setup_test_environment`` replaces
    it with ``['*']`` for the duration of a test run, which is the one state in
    which this cannot happen.
    """
    with override_settings(ALLOWED_HOSTS=['testserver']):
        response = client.get('/', HTTP_HOST='evil.example.com')

    assert response.status_code == 400

    written = request_log.getvalue()

    assert 'django.security.DisallowedHost' in written
    assert 'evil.example.com' in written
