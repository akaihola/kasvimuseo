==============================================================================
Issue 057: A disclosed ``SECRET_KEY`` runs code, because sessions are pickled
==============================================================================

:Status: Fixed
:Severity: High
:Area: settings / security
:Reported: 2026-08-02
:Source: Reading ``docs/upgrade-plan.rst`` Stage 1, which names
    ``SESSION_SERIALIZER`` as a hardening step "this project could take at any
    time" and then, correctly, leaves it out of that stage. What makes it an
    issue rather than a footnote is 049: the key the pickle is trusted on is
    disclosed *today*
:Evidence: kasvimuseo/tests/test_settings_session_serializer.py -- three tests,
    two of them behavioural. Before the fix all three failed, and the two that
    read what the session backend actually wrote failed with
    ``UnicodeDecodeError: 'utf8' codec can't decode byte 0x80 in position 0``
    -- ``0x80`` being the pickle protocol 2 opcode, which is the defect itself
    rendered as a test failure
:Depends on: (none) -- it is one setting in a file this repository owns, and it
    is deliberately **not** ordered behind 049: the point is that it holds
    whether or not the key is ever rotated
:Blocks: (none)
:Related: 025 -- where the ``SECRET_KEY`` left the tracked files, and where the
    disclosure this issue escalates is described
    049 -- the half of 025 that is still open, and the reason the precondition
    for the escalation is satisfied in production right now; also the
    maintenance window this change should ride
    036 -- the end-of-life stack this sits inside; Django 1.6 makes the JSON
    serializer the default, so upgrade Stage 2 would have brought it eventually
:Decision: Take it now, in ``ylaneenkasvit/common_settings.py``, rather than waiting for the upgrade to bring it or for 049 to remove its precondition. Three things settled that. It is one line and it has no design in it: Django 1.6 chose the same value for every project, and the upgrade plan reaches 1.6 at Stage 2 with this setting already correct rather than as a behaviour change to notice. Nothing this project stores in a session needs pickle -- checked rather than assumed, and the check is written out under "What is in a session here". And the cost it does have, one round of logouts, is the cost 049 already carries, so the two ride the same maintenance window and the second one is free. The alternative -- leave it, on the grounds that the exploit needs a key the maintainer is about to rotate -- was rejected because "about to" is exactly what 049's ``Decision`` field cannot yet say: its timing belongs to the customer, and until they name it the window is open. Ordering this behind 049 would also invert the value: the whole point of a serializer that cannot execute code is that it holds for the *next* key disclosure too.
:Resolution: 41774eb -- ``SESSION_SERIALIZER`` in ``common_settings.py`` with the reason beside it, and ``kasvimuseo/tests/test_settings_session_serializer.py``. The server-side acts of 049, 050 and 051 are untouched and still open; this only removes what a disclosed key is worth.

Problem
=======

``django.contrib.sessions`` is in ``INSTALLED_APPS`` and no settings module in
this repository set ``SESSION_SERIALIZER``::

    $ grep -rn SESSION_ ylaneenkasvit/*.py
    $                                       # nothing, before this change

So the installed Django's default applied. Read from the container rather than
from memory::

    >>> import django; django.get_version()
    '1.5.12'
    >>> from django.conf import global_settings
    >>> global_settings.SESSION_SERIALIZER
    'django.contrib.sessions.serializers.PickleSerializer'

``PickleSerializer`` is the pre-1.5.3 behaviour, kept as the default through
the whole 1.5 series; 1.6 changed it to ``JSONSerializer``.

What that means in this application is a two-step chain, and neither step is a
bug on its own:

1. The session cookie carries a session **key**, and the payload lives in
   ``django_session``. The payload is stored as
   ``b64encode(hmac_hexdigest + ':' + serialized)``, and the HMAC is keyed on
   ``SECRET_KEY``. ``SessionBase.decode`` verifies that HMAC and then hands the
   rest to the serializer -- ``pickle.loads``, here.
2. ``SECRET_KEY`` is disclosed. It was committed to this repository (issue
   025), and per issue 049 the running server still signs with it: the rotated
   value is in the vault and not in the process environment.

Anybody who has ever cloned this repository can therefore write a row into a
session -- or forge the signed payload wherever one is accepted -- whose
unpickling runs code. Pickle is not a data format; ``__reduce__`` is a call.

Impact
======

This does not open a hole. It changes what the hole that is already open is
worth.

Issue 049's impact is stated as "anybody who has ever had a clone of this
repository can forge a session cookie for any account, including a superuser".
That is authentication bypass: the attacker becomes a superuser of this
application, and a superuser of this application can edit garden records.

With the pickle serializer the same attacker instead gets **arbitrary code
execution as the uWSGI user**, which is a different thing entirely: the
database password, the media tree, the rest of the host, and any credential
that process can reach. The application's own permission model stops being the
boundary.

Severity is ``High`` for that reason, and the argument for it is worth stating
plainly because it cuts both ways:

* Against ``High``: this is not a standalone remote hole. The exploit needs
  ``SECRET_KEY``. On a deployment whose key has never leaked, the pickle
  default is a latent weakness and nothing more, and that is exactly why
  Django could leave it as the default through 1.5.
* For ``High``, and this is what decides it: the precondition is not
  hypothetical here, it is the subject of an open ``High`` issue with no date
  on it. 049 says the disclosure is live "for as long as this is open", and
  049's timing belongs to the customer. Ranking this ``Medium`` would be
  ranking it as if the key were secret.

So it is an escalation of 025 and 049 rather than a finding of its own, and its
severity is inherited from them and multiplied by what pickle adds.

What is in a session here
=========================

JSON cannot carry arbitrary objects, so the switch is only safe if everything
this application puts in a session is JSON-serialisable. Everything that writes
to a session in the installed applications was read, not assumed:

``django.contrib.auth``
    ``_auth_user_id`` is ``user.pk``, an integer, and ``_auth_user_backend`` is
    a dotted path, a string. ``set_test_cookie`` writes the string
    ``'worked'``. All JSON.

``django.contrib.messages``
    ``MESSAGE_STORAGE`` is unset, so it is Django 1.5's default,
    ``FallbackStorage`` -- cookie first, session only for messages too large
    for the cookie. This is the one that had to be checked properly, because
    a ``Message`` is not a JSON type. Django 1.5's
    ``messages/storage/session.py`` already handles it::

        def _store(self, messages, response, *args, **kwargs):
            if messages:
                self.request.session[self.session_key] = \
                    self.serialize_messages(messages)

    ``serialize_messages`` is ``MessageEncoder(...).encode(messages)``, so what
    reaches the session is a JSON **string**. The session serializer sees a
    string. (This is worth knowing rather than guessing: the round trip is the
    third test in the evidence file, with ``MESSAGE_STORAGE`` forced to
    ``SessionStorage`` so the fallback branch is the one exercised.)

``django.contrib.admin``
    Writes nothing to the session of its own; its user-facing state is
    messages, above.

``grappelli`` and ``grappelli.dashboard``
    The only ``request.session`` in the installed grappelli is inside a
    docstring in ``dashboard/modules.py`` -- the "build a history module" example.
    ``ylaneenkasvit/dashboard.py`` builds ``ModelList``, ``LinkList`` and
    ``RecentActions`` modules, none of which touch the session.

``photologue``, ``south``, ``jqm``
    Nothing.

This project's own code
    ``grep -rn 'request\.session\|\.session\['`` over ``kasvimuseo/`` and
    ``ylaneenkasvit/`` finds no writes outside the tests. The label editor and
    its API authenticate through the session but store nothing in it.

``django.contrib.formtools``
    Its wizard has a session storage backend that would store form data
    directly, and it is the one place a non-JSON value could plausibly appear
    -- but formtools is not in ``INSTALLED_APPS`` and nothing here has a
    wizard.

Nothing had to be excluded, and nothing had to be converted.

The fix
=======

``ylaneenkasvit/common_settings.py``::

    SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

with the reason in a comment above it, so that the next reader knows it is
guarding something rather than restating a default.

``common_settings`` is where production reads it. The chain is
``ylaneenkasvit/ylaneenkasvit_settings.py`` (and ``kajala_settings.py`` for the
second site), each of which begins ``from .common_settings import *`` and then
overrides the site-specific values, with an optional untracked
``local_settings`` on top -- and ``test_settings.py`` builds on
``common_settings`` too, deliberately, so the suite sees the same value the
server does. ``settings.py`` is a one-line stub for ``manage.py`` and holds
nothing. Putting the setting in the common module therefore covers both sites,
the development server and the tests with one line, and no site-specific file
overrides it.

What it costs
=============

**Every existing session is invalidated.** A session stored as a pickle cannot
be read back by the JSON serializer, so on the next deploy everybody logged in
to production is logged out once and logs back in normally. Sessions are the
only thing affected: password-reset links, CSRF tokens and other
``django.core.signing`` payloads do not go through the session serializer and
are unchanged by this.

That is the same cost issue 049 carries, from a different cause -- 049 changes
the key that the sessions are signed with, this changes the format they are
stored in, and either one alone logs everybody out. **So the two should ride
the same maintenance window**, and the second one is then free.

The runbook for that window is ``ansible/secure-production.yaml``, added by
commit ``bf98b6f`` for issues 049, 050 and 051, and documented in ``README.rst``
under "The security maintenance window". This change needs no step of its own
there: it is ordinary code, so the ``install.yaml`` import that the playbook
already begins with deploys it, and the uWSGI restart that 049 needs is the one
that picks it up. Nothing about that playbook changes, and the ``Status`` of
049, 050 and 051 is untouched -- what they are waiting for is a date, and this
issue does not supply one.

**It is not a substitute for rotating the key.** A forged session cookie still
authenticates as any account while the old key is in use; what this removes is
the step from that to running code. 049 is still ``High`` and still open.

Verification
============

* ``dev/kasvimuseo app test`` -- 433 tests pass. Reverting the one settings
  line fails exactly the three new ones, two of them on the pickle opcode
  rather than on a string comparison, which is what makes them a regression
  test rather than a restatement of the setting.
* ``dev/kasvimuseo app browser-test`` -- the browser suite logs into the admin
  and drives the label editor, so a real session is created, stored, read back
  on the next request and used to authorise a save.
* **Against the restored production dump**, which is the check the suite cannot
  make: with ``.dev/backups/production.sql`` loaded, logging into the admin,
  loading the species changelist and saving a record -- which produces a
  message through ``FallbackStorage`` -- all work, with no session error and
  the "changed successfully" message rendered on the page it redirects to. The
  dump's ``django_session`` rows, written by the pickle serializer on the
  server, are simply not readable and are discarded as expired sessions are:
  that is the logout described above, observed rather than predicted.
