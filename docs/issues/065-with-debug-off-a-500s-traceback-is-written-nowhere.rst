==============================================================================
Issue 065: With ``DEBUG`` off, a 500's traceback is written nowhere
==============================================================================

:Status: Fixed
:Severity: Medium
:Area: settings / operations
:Reported: 2026-08-02
:Source: Reading ``ylaneenkasvit/common_settings.py``'s ``LOGGING`` block
    beside issue 051. 051 is about to turn ``DEBUG`` off on the production
    server, and ``DEBUG`` is the only reason a traceback is visible anywhere
    today: ``grep -rn 'EMAIL_\|LOGGING' ylaneenkasvit/*.py`` finds one stock
    logging block and no ``EMAIL_*`` setting at all, and
    ``grep -rniE 'postfix|msmtp|sendmail|exim|smtp' ansible/`` returns nothing
:Evidence: kasvimuseo/tests/test_settings_logging.py -- seven tests, of which
    five failed before the change. The two that matter are behavioural: each
    installs the configuration ``common_settings`` describes with the console
    handler's stream pointed at a buffer, provokes the thing Django logs, and
    reads the buffer. Before the change they failed with
    ``assert 'Internal Server Error: /crash/' in ''`` and
    ``assert 'django.security.DisallowedHost' in ''`` -- the empty string being
    the defect itself rendered as a test failure. Measured through a running
    server as well, on Django 1.6.11 in the container with
    ``KASVIMUSEO_DEBUG`` unset: a ``GET`` of a deliberately raising URL
    returned ``templates/500.html`` and gunicorn's output carried the
    access-log line and nothing else
:Depends on: (none) -- it is one handler, two loggers and a root logger in a
    file this repository owns, and it is deliberately **not** ordered behind 051: it is
    what makes 051 safe to perform, not the other way round
:Blocks: (none) -- it is fixed here, so it blocks nothing. Had it not been, it
    would have been a precondition for 051 rather than a consequence of it:
    turning ``DEBUG`` off with this configuration in place trades a traceback
    on the visitor's screen for a traceback nowhere at all
:Related: 051 -- the change that makes this bite. Production runs with
    ``DEBUG`` on, which is why an error is visible at all today, and 051 is the
    act that removes that
    044 -- why the development server is gunicorn, which is what the
    reproduction below runs, and why its output is where a traceback is looked
    for
    025 -- how the deployment passes anything into the application at all: the
    environment of the uWSGI process, written by Ansible into ``uwsgi.ini``.
    An ``EMAIL_HOST`` would arrive the same way, which is 066
    026 -- the same mechanism, and the issue that established it for a
    non-secret value
    057 -- the same file and the same shape of argument: a Django default that
    is wrong for this deployment
    059 -- likewise, and the issue whose own server-side complement (060) was
    filed separately rather than grown into it, which is what 066 is here
    066 -- the deployment half: nothing on the server can deliver the mail this
    configuration still tries to send
    036 -- the upgrade programme. Stage 3 landed Django 1.6.11 while this was
    being written, and it brought a second logger with the same defect --
    ``django.security`` -- which is why the fix names two
:Decision: Add a stream handler and a root logger to ``LOGGING`` in ``ylaneenkasvit/common_settings.py``, unfiltered by ``DEBUG``, give it to ``django.request`` and to Django 1.6's ``django.security``, and keep ``mail_admins``. Three things settled the shape. stderr is where both of this project's servers already keep a log -- uWSGI writes it to ``/home/<app_user>/uwsgi.error.log`` through ``logger = file:`` in ``ansible/roles/akaihola.uwsgi/templates/uwsgi.ini``, and the development gunicorn writes it to the container's output -- so a stream handler needs nothing on the server to exist and no new file for anybody to rotate. A file handler was considered and rejected for exactly that: it would put a second log beside ``uwsgi.error.log``, owned by the application rather than by the process manager, with a path this repository would have to invent and Ansible would have to create. And the handler carries no ``RequireDebugTrue`` filter, which is the whole point: Django's own ``DEFAULT_LOGGING`` has one, and that filter is why this configuration looks fine today and stops working the moment 051 is acted on. ``mail_admins`` stays, and that is the one part of this that is a judgement rather than a repair -- see "Why ``mail_admins`` stays" below. Nothing is added to ``ansible/``: an MTA and an ``EMAIL_HOST`` are a decision about the server, they are 066, and this issue is the half that can be finished here.
:Resolution: 238b35e -- ``LOGGING`` in ``common_settings.py`` with the reasoning beside it, the explicit quiet in ``test_settings.py``, and ``kasvimuseo/tests/test_settings_logging.py``. Nothing in ``ansible/`` changed and the status of 051 is untouched; the mail half is 066, filed with this and still open.

Problem
=======

``ylaneenkasvit/common_settings.py`` defined ``LOGGING`` as Django's stock
project-template block and nothing more: one filter, one handler and one
logger. The handler is ``django.utils.log.AdminEmailHandler``, filtered by
``RequireDebugFalse``, and the logger is ``django.request`` at ``ERROR``. There
is no console handler, no file handler and no root logger.

The installed Django is 1.6.11 since upgrade plan Stage 3, and 1.6 makes this
worse rather than better: its ``DEFAULT_LOGGING`` adds a ``django.security``
logger with ``mail_admins`` alone and ``propagate: False``, so every
``SuspiciousOperation`` -- a ``Host`` header the ``ALLOWED_HOSTS`` of issue 026
refuses, a tampered signed cookie -- goes the same nowhere a 500 does. That
logger is new, this repository never configured it, and it inherited the
defect.

No settings module in this repository sets any ``EMAIL_*`` setting::

    $ grep -rn 'EMAIL_' ylaneenkasvit/*.py
    $                                       # nothing

so ``AdminEmailHandler`` uses Django's defaults, read from the container rather
than from memory::

    >>> settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_BACKEND
    ('localhost', 25, 'django.core.mail.backends.smtp.EmailBackend')

and ``ansible/`` installs no MTA -- no postfix, msmtp, sendmail or exim in
``install.yaml``, ``secure-production.yaml``, any role or any vars file. In the
same container::

    >>> socket.create_connection(('localhost', 25), 2)
    error: [Errno 111] Connection refused

Django swallows that. ``AdminEmailHandler.emit`` ends in
``mail.mail_admins(subject, message, fail_silently=True, ...)``, and
``fail_silently`` reaches the SMTP backend's ``open()``, which returns instead
of raising. So the handler does not raise, ``logging.Handler.handle`` never
calls ``handleError``, and ``logging.raiseExceptions`` -- which is ``True``,
and which would otherwise print the *handler's* traceback to stderr -- is never
consulted. The record is dropped in silence, with no line anywhere saying that
a handler failed.

Nor does Python's other safety net apply. "No handlers could be found for
logger" is printed once per logger, and only when a record reaches
``callHandlers`` and finds no handler on the whole chain. ``django.request``
has one -- ``mail_admins`` -- so a handler *is* found; that it then filters or
discards the record is not something the check can see. ``disable_existing_loggers:
False`` changes nothing here either: it governs whether loggers Django's
``DEFAULT_LOGGING`` pass created are switched off, not whether a message is
printed about a logger with no handler at all.

Why it is invisible today
-------------------------

Django applies its own ``DEFAULT_LOGGING`` before the project's ``LOGGING``
(``django/conf/__init__.py``, ``LazySettings._configure_logging``), and
``DEFAULT_LOGGING`` puts a ``logging.StreamHandler`` on the ``django`` logger
behind a ``RequireDebugTrue`` filter. Production runs with ``DEBUG = True``
(issue 051), so a 500's traceback does reach stderr today and this looks like a
configuration that works. Read out of the running configuration on Django
1.6.11, with ``DEBUG`` off::

    django.request   level=40 propagate=True  handlers=[('AdminEmailHandler', ['RequireDebugFalse'])]
    django.security  level=40 propagate=False handlers=[('AdminEmailHandler', ['RequireDebugFalse'])]
    django           level=0  propagate=1     handlers=[('StreamHandler', ['RequireDebugTrue'])]
    py.warnings      level=0  propagate=1     handlers=[('StreamHandler', ['RequireDebugTrue'])]
    (root)           level=30 propagate=1     handlers=[]
    EMAIL_* : localhost:25 via django.core.mail.backends.smtp.EmailBackend
    port 25 : [Errno 111] Connection refused

Turn ``DEBUG`` off and every path closes at once: the filter drops the console
copy, the mail is refused and swallowed, and nothing else is listening. In the
same process, an ``ERROR`` logged to ``django.request`` and one logged to
``django.security.DisallowedHost`` both printed nothing at all.

The reproduction
================

A temporary URL that raises, wired into ``ylaneenkasvit/urls.py`` for the
measurement and not committed::

    (r'^boom/$', lambda request: 1 / 0),

served by the same gunicorn ``dev/kasvimuseo app run`` uses (issue 044), in the
application's own container, with ``KASVIMUSEO_DEBUG`` unset -- which is what
sets ``DEBUG`` (``common_settings.py``). The response::

    $ curl -si http://127.0.0.1:8231/boom/ | head -5
    HTTP/1.1 500 INTERNAL SERVER ERROR
    Server: gunicorn/0.17.4
    ...
    500 - Django server error

which is ``ylaneenkasvit/templates/500.html``. The server's entire output for
that request, on Django 1.6.11 with this issue's configuration::

    "127.0.0.1 - - [03/Aug/2026:06:21:13] "GET /boom/ HTTP/1.1" 500 - "-" "curl/8.21.0"

One access-log line. No traceback in the response, none on stderr, and no file
written -- there is no file handler to write one. The same request with
``KASVIMUSEO_DEBUG=1``, which is how production runs today, prints
``Internal Server Error: /boom/`` and the full traceback, from the handler that
the ``RequireDebugTrue`` filter is about.

Impact
======

An unhandled exception in production leaves no evidence. The visitor gets a
static 500 page, the operator gets nothing at all, and the defect is reported
-- if it is reported -- as "the page did not work", from a garden, some days
later. Every issue in this register that was diagnosed from a traceback would
have been diagnosed from nothing.

This is latent rather than active, and the severity says so. Today ``DEBUG``
is on, so the traceback is on the visitor's screen: that is issue 051's
complaint and it is a live information disclosure, not an observability gap.
This issue is what the state after 051 looks like, and it is ``Medium`` for
that reason -- nothing a user can see is wrong, and nothing is wrong at all
until a server-side act on the maintainer's timetable is performed. It is not
``Low``, because the moment that act is performed the next production defect
becomes one nobody can read; and calling it ``High`` would be overstating a
problem that does not exist yet on a page whose ``High`` entries are all live
disclosures.

What changed
============

``ylaneenkasvit/common_settings.py``, in ``LOGGING``:

* a ``console`` handler -- ``logging.StreamHandler`` at ``WARNING``, with a
  formatter carrying the timestamp, level and logger name, because uWSGI writes
  a worker's stderr through verbatim and adds none of them;
* ``django.request`` gets it alongside ``mail_admins``, and ``propagate`` goes
  from ``True`` to ``False``. ``False`` is what Django's own ``DEFAULT_LOGGING``
  says; with ``console`` named on the logger, propagating would hand the same
  record to the ``django`` logger's handler and then to ``root``, and print a
  traceback two or three times under ``DEBUG``;
* ``django.security`` gets the same pair. It is Django 1.6's logger and it
  had the same defect, and it is named here rather than left to inherit from
  ``django`` below: what it would inherit depends on an entry that looks
  removable, and removing that entry would silently put it back to mailing
  ``localhost:25`` and nothing else;
* a ``root`` logger at ``WARNING`` with the same handler, for everything that
  is not a request -- a management command, South, a third-party package's own
  logger. ``WARNING`` rather than ``INFO`` because this is a log nobody reads
  until something is wrong. ``django.request`` logs every 404 at ``WARNING``
  and does not reach it, being handled at ``ERROR`` above;
* ``django`` and ``py.warnings`` are given empty handler lists.
  ``DEFAULT_LOGGING`` puts its ``RequireDebugTrue`` console handler on both,
  and with a root handler present that is a second copy of every warning
  whenever ``DEBUG`` is on -- measured: the ``django.conf.urls.defaults``
  deprecation appeared twice on the development server's output before this,
  once after. Naming ``django`` also hands the loggers under it that this
  dictionary does not name -- ``django.db.backends`` and the rest -- back their
  defaults, so they reach ``root`` rather than keeping whatever the
  ``DEFAULT_LOGGING`` pass gave them.

After the change, the same request on the same server::

    2026-08-02 23:44:12,944 ERROR django.request: Internal Server Error: /boom/
    Traceback (most recent call last):
      File ".../django/core/handlers/base.py", line 113, in get_response
        response = callback(request, *callback_args, **callback_kwargs)
      File "/src/ylaneenkasvit/urls.py", line 36, in <lambda>
        (r'^boom/$', lambda request: 1 / 0),
    ZeroDivisionError: integer division or modulo by zero
    "127.0.0.1 - - [02/Aug/2026:23:44:12] "GET /boom/ HTTP/1.1" 500 - "-" "curl/8.21.0"

On the production host that stream is ``/home/<app_user>/uwsgi.error.log``.

Why ``mail_admins`` stays
=========================

Nothing can deliver it, and a handler that fails silently is its own defect --
that is the argument for deleting it, and it was taken seriously rather than
waved away. Three things answered it.

It cannot lose anything. The traceback is on ``console`` first, on a handler
that has nowhere to fail to; ``mail_admins`` is a second copy of a record that
is already written down. Before this change it was the *only* copy, which is
what made its silent failure a defect. It is now the difference between one
place and two.

It costs one refused connection to ``localhost:25`` per 500, which is a
``connect()`` to a loopback address that returns ``ECONNREFUSED`` immediately.
A site that is raising often enough for that to matter has a larger problem
than this handler.

And it is the only handler here that reaches a person who is not already
reading a log file. The day the server gets an MTA, or an ``EMAIL_HOST``
pointing at a relay -- which is 066, filed with this issue -- it starts working
with no change to this file. Deleting it now and adding it back then would buy
nothing except the need to remember.

What makes that a decision rather than an oversight is that it is written down:
the comment beside it in ``common_settings.py`` says it is inert and why, and
``test_settings_logging.py`` asserts both that it is still configured and that
``EMAIL_HOST`` is still Django's default -- so if a settings module ever does
point the mail somewhere real, the test fails and the comment gets rewritten.

Development and test settings
=============================

``ylaneenkasvit/local_settings.development.py`` needed nothing. It sets
``DEBUG = True``, and before this change that is what put a traceback on the
development server's output, through ``DEFAULT_LOGGING``'s filtered handler;
after it, the same traceback arrives through ``console``, once, with a
timestamp and a logger name in front of it. What changed in development is that
the output no longer depends on ``DEBUG`` -- which is the property this issue
is about, seen from the other end.

``ylaneenkasvit/test_settings.py`` needed a change, and understanding the line
that was there came first. It said::

    # Don't try to mail admins about exceptions raised inside tests.
    LOGGING = dict(LOGGING, loggers={})

The intent is right and the mechanism does not do it. Django applies
``DEFAULT_LOGGING`` before the project's ``LOGGING``, and
``disable_existing_loggers: False`` means a logger the project's dictionary
does not *name* keeps whatever the first pass gave it. ``loggers={}`` names
nothing, so ``django.request`` kept ``DEFAULT_LOGGING``'s
``AdminEmailHandler`` through every run of this suite -- read out of a test
run, before this change::

    django.request handlers=[AdminEmailHandler]

The only reason that never opened a connection to ``localhost:25`` is that
Django's test runner swaps in the locmem email backend. Left as it was, the new
root handler would also have survived, and the suite would have printed the
traceback of every deliberately broken request it makes.

So the loggers are named and given empty handler lists, with ``root`` alongside
them. The suite is as quiet as it was -- 462 tests, no traceback in the output
-- and it is quiet because this file says so rather than because of what a
previous ``dictConfig`` pass happened to leave behind.

Verification
============

``kasvimuseo/tests/test_settings_logging.py``. Against the configuration this
issue describes::

    kasvimuseo/tests/test_settings_logging.py FFF..FF
    E   AssertionError: django.request has no handler that writes anywhere:
        ['django.utils.log.AdminEmailHandler']
    E   KeyError: u'django.security'
    E   KeyError: u'console'
    E   AssertionError: assert 'Internal Server Error: /crash/' in ''
    E   AssertionError: assert 'django.security.DisallowedHost' in ''
    5 failed, 2 passed

The last two are the behavioural ones, and the empty strings are the issue.
The two that pass are the two about ``mail_admins``: it was configured before
this change and it is configured after, which is the point of asserting it --
they are there so that removing it later is a decision somebody makes rather
than a tidy-up, and they would not have failed either way.

After the change, seven pass, and the whole suite is 462 passed with no
traceback in its output. ``dev/kasvimuseo app coverage`` reports 98 % and exits
0, so the floor 064 installed is met with the new module in the tree, and
``dev/kasvimuseo app browser-test`` is 54 passed and 6 skipped -- the six
WebKit touch drags of 061 -- in both engines.

See also
========

:doc:`051 <051-production-serves-with-debug-on-behind-an-untracked-local-settings>`
-- the act this makes safe. Its ``Status`` is untouched here: turning ``DEBUG``
off is a server-side act on the maintainer's timetable, and this issue only
changes what the server will do afterwards.
:doc:`066 <066-nothing-on-the-production-host-can-deliver-mail_admins>` -- the
deployment half, filed separately and still open.
