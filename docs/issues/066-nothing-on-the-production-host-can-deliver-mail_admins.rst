==============================================================================
Issue 066: Nothing on the production host can deliver ``mail_admins``
==============================================================================

:Status: Open
:Severity: Low
:Area: deployment / operations
:Reported: 2026-08-02
:Source: Filed out of issue 065, which is the application half of the same
    question. 065 gave ``django.request`` a handler that writes to stderr, and
    in doing so had to rule on whether the ``mail_admins`` handler beside it
    was worth keeping. It is kept, and it is inert: nothing on the server can
    deliver what it sends
:Evidence: (none) -- there is no test, and this repository has no way to write
    one: the delivery would happen on the production host and nothing here
    exercises it. ``grep -rniE 'postfix|msmtp|sendmail|exim|smtp|mailutils'
    ansible/`` returns nothing and ``grep -rn 'EMAIL_' ylaneenkasvit/*.py``
    returns nothing, which together are the whole of the observation.
    ``kasvimuseo/tests/test_settings_logging.py`` asserts the second half of it
    -- that ``EMAIL_HOST`` is still Django's ``localhost`` -- so that pointing
    the mail somewhere real fails a test rather than passing unnoticed
:Depends on: (none) -- but see ``Decision``: it is a change to the running
    server, so it lands on a deploy, like 049, 051 and 060
:Blocks: (none)
:Related: 065 -- the application half, fixed. That change means a traceback is
    written down whatever happens here, which is what turns this from a defect
    into an improvement
    060 -- the same shape: an application-side issue was fixed and the
    server-side complement was filed on its own rather than grown into it
    025 -- how anything reaches the application on the server at all: the
    environment written into ``uwsgi.ini`` by Ansible. An ``EMAIL_HOST`` would
    arrive the same way, and a relay's credentials would be a vaulted value
    like the ones 025 moved
    026 -- the same mechanism for a value that is not a secret, which is what a
    host name is
:Decision: undecided. There are three answers and they are not the same size. (1) Install an MTA -- postfix or msmtp -- in ``ansible/install.yaml``, so ``localhost:25`` accepts mail. That is a new daemon, or at least a new package with a relay configuration, on a host whose whole point is that it is small. (2) Set ``EMAIL_HOST`` (and, if the relay wants them, ``EMAIL_HOST_USER``, ``EMAIL_HOST_PASSWORD`` and ``EMAIL_USE_TLS``) from the uWSGI environment, pointing at a relay that already exists elsewhere. That is the cheaper one and it fits the mechanism this deployment already has, but it needs a relay to name and, if it authenticates, a vaulted credential. (3) Decide that ``uwsgi.error.log`` is enough and delete the ``mail_admins`` handler, which makes the register honest at the cost of the only path that reaches somebody who is not reading a log file. Which of these is right depends on something this repository cannot see: whether the maintainer wants to be told, or is content to look. That is the ruling this field is waiting for.
:Resolution: (none)

Problem
=======

``ylaneenkasvit/common_settings.py`` sends a 500's traceback to two handlers.
One writes it to stderr, which uWSGI keeps in
``/home/<app_user>/uwsgi.error.log`` (issue 065). The other is
``django.utils.log.AdminEmailHandler``, and on this host it does nothing at
all.

``AdminEmailHandler`` sends through Django's mail machinery, and no settings
module in this repository sets any ``EMAIL_*`` setting, so the defaults apply:
the SMTP backend, ``localhost``, port 25. Nothing in ``ansible/`` installs
anything that listens there -- not ``install.yaml``, not
``secure-production.yaml``, not a role and not a vars file. The connection is
refused, and ``AdminEmailHandler.emit`` passes ``fail_silently=True``, so the
refusal is swallowed: no exception, no ``handleError``, no line in any log
saying that a handler failed.

The one thing this is not is a lost traceback. Since 065 the same record is
written to stderr first, by a handler that cannot fail to deliver, so what is
missing here is a notification and not the evidence.

What to do
==========

One of the three in ``Decision``, and the choice is the work. Two of them are
small once chosen:

* An ``EMAIL_HOST`` for the application would go where every other environment
  value goes -- ``ansible/roles/akaihola.uwsgi/templates/uwsgi.ini``, from
  ``ansible/vars/main.yml``, exactly as ``KASVIMUSEO_ALLOWED_HOSTS`` does
  (issue 026) -- with ``common_settings.py`` reading it and falling back to the
  current behaviour when it is unset, so a development checkout and the test
  suite are unaffected.
* An MTA would be a package and a configuration file in ``install.yaml``, and
  a decision about what it is allowed to send and to whom.

Whichever is taken, the comment beside ``mail_admins`` in
``common_settings.py`` and the two assertions in
``kasvimuseo/tests/test_settings_logging.py`` are written on the assumption
that it is inert, and they are what will notice: the test that asserts
``EMAIL_HOST == 'localhost'`` fails as soon as this issue is acted on, which is
deliberate.

If the answer is (3) -- delete the handler -- then nothing on the server
changes and this issue closes as ``Rejected`` with that reasoning, the handler
and its comment come out of ``common_settings.py``, and ``uwsgi.error.log``
becomes the only place a production error is ever recorded. That is a real
option rather than a straw man: it is one fewer thing that looks like it works.

See also
========

:doc:`065 <065-with-debug-off-a-500s-traceback-is-written-nowhere>` -- the
application half, and where the reasoning for keeping the handler at all is
written out.
