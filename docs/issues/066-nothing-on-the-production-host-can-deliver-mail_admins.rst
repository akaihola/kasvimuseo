==============================================================================
Issue 066: Nothing on the production host can deliver ``mail_admins``
==============================================================================

:Status: Rejected
:Severity: Low
:Area: deployment / operations
:Reported: 2026-08-02
:Source: Filed out of issue 065, which is the application half of the same
    question. 065 gave ``django.request`` a handler that writes to stderr, and
    in doing so had to rule on whether the ``mail_admins`` handler beside it
    was worth keeping. It is kept, and it is inert: nothing on the server can
    deliver what it sends
:Evidence: (none for the defect) -- there was no test and this repository had
    no way to write one: the delivery would have happened on the production
    host and nothing here exercises it. ``grep -rniE
    'postfix|msmtp|sendmail|exim|smtp|mailutils' ansible/`` returned nothing
    and ``grep -rn 'EMAIL_' ylaneenkasvit/*.py`` returned nothing, which
    together were the whole of the observation. What is pinned now is the
    ruling instead: ``kasvimuseo/tests/test_settings_logging.py`` has
    ``test_nothing_here_mails_an_error``, which fails if any handler in
    ``LOGGING`` is an ``EmailHandler`` again, and
    ``test_no_settings_module_points_the_mail_anywhere``, which keeps the old
    assertion that ``EMAIL_HOST`` is still Django's ``localhost``. The first
    replaces ``test_mail_admins_is_still_configured``, which asserted the
    opposite and was written so that deleting the handler would be a decision
    rather than a tidy-up -- this is that decision, so the assertion is turned
    around rather than dropped
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
:Decision: **(3), by the maintainer, on 2026-08-04.** The three answers were not the same size. (1) Install an MTA -- postfix or msmtp -- in ``ansible/install.yaml``, so ``localhost:25`` accepts mail. That is a new daemon, or at least a new package with a relay configuration, on a host whose whole point is that it is small. (2) Set ``EMAIL_HOST`` (and, if the relay wants them, ``EMAIL_HOST_USER``, ``EMAIL_HOST_PASSWORD`` and ``EMAIL_USE_TLS``) from the uWSGI environment, pointing at a relay that already exists elsewhere. That is the cheaper one and it fits the mechanism this deployment already has, but it needs a relay to name and, if it authenticates, a vaulted credential. (3) Decide that ``uwsgi.error.log`` is enough and delete the ``mail_admins`` handler, which makes the register honest at the cost of the only path that reaches somebody who is not reading a log file. Which of these was right depended on something this repository cannot see -- whether the maintainer wants to be *told* about a 500, or is content to *look* -- so it was asked, in exactly those terms, and the answer was (3): ``uwsgi.error.log`` is enough. That is the ruling, and it is the maintainer's rather than an inference from the evidence. The evidence supports it and does not compel it: since 065 the traceback is on stderr whatever happens here, so what was being weighed was a notification nobody had asked for against a handler that has never once delivered anything. What the ruling buys is honesty -- one fewer thing in the settings that looks like it works -- and what it costs is that a 500 is now something somebody has to go and look for. Both halves were on the table when it was taken. This is the one option that cannot be undone by a deploy, which is why it waited for the answer rather than being ruled on the evidence: the wiring for (2) was written first, as the reversible half, and is withdrawn unmerged now that (3) is the answer -- it is on the tag ``interim-email-wiring-066`` if it is ever wanted.
:Resolution: **Rejected** -- the defect is real and the fix is to stop claiming to do the thing. The ``mail_admins`` handler, its ``AdminEmailHandler`` class and the ``require_debug_false`` filter that existed only to serve it are gone from ``LOGGING`` in ``ylaneenkasvit/common_settings.py``; ``django.request`` and ``django.security`` keep the ``console`` handler 065 gave them, so ``/home/<app_user>/uwsgi.error.log`` is now the only place a production error is recorded, and that is the whole of the promise. Nothing in ``ansible/`` changed: no MTA is installed and no ``EMAIL_*`` is set, which is what makes this a rejection rather than a fix. The commit is 8c8ba48

Problem
=======

As reported, and in the present tense it was written in. What it describes is
the state before the change under "What changed" below, which removed the
second of the two handlers.

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

What changed
============

Nothing on the server, which is the point of a rejection: the act was to stop
the settings claiming something the deployment does not do.

Out of ``LOGGING`` in ``ylaneenkasvit/common_settings.py``:

* the ``mail_admins`` handler, ``django.utils.log.AdminEmailHandler`` at
  ``ERROR``;
* its ``require_debug_false`` filter, and with it the whole ``filters`` key --
  that filter was in the block only to stop the mail being sent while ``DEBUG``
  was on, and nothing else here used it;
* the two references to it, in ``django.request`` and ``django.security``. Both
  keep the ``console`` handler 065 gave them, and both keep ``propagate:
  False`` for the reason 065 gives, which is unaffected.

The comment beside it is replaced rather than deleted. It used to argue why the
handler stayed; it now records that it was taken out, on whose ruling, and what
the two alternatives were -- so that a later reader finds a decision instead of
wondering why this project's block differs from Django's stock one. The stock
block *has* an ``AdminEmailHandler``, so an absence with no note beside it
reads as an oversight and invites a copy-paste to put it back.

In ``kasvimuseo/tests/test_settings_logging.py``,
``test_mail_admins_is_still_configured`` becomes
``test_nothing_here_mails_an_error``. That is the assertion working as
designed: it existed so that removing the handler would be a decision somebody
took rather than a tidy-up, this is that decision, and the test is turned
around to guard the new state rather than dropped. It checks every handler in
the dictionary, not only the ones the two loggers name, because a mailing
handler defined and left unreferenced is the same defect one edit later.
``test_no_settings_module_points_the_mail_anywhere`` keeps the old
``EMAIL_HOST == 'localhost'`` assertion, which still says something worth
saying: there is no relay either.

Nothing in ``ansible/`` changed -- no MTA, no ``EMAIL_*`` -- which is what
separates this from the other two answers.

What this costs
===============

A 500 in production is now something somebody has to go and look for. There is
no path from an unhandled exception to a person who is not reading
``uwsgi.error.log``, and this issue is the record that that is deliberate
rather than an omission.

What it does not cost is the traceback. Since 065 the record reaches stderr
through a handler that has nowhere to fail to, and uWSGI writes that to
``/home/<app_user>/uwsgi.error.log`` -- so the evidence is written down exactly
as it was the day before this change. What is gone is a second copy that was
never once delivered.

If a notification is ever wanted, two things come back together: the handler,
and an ``EMAIL_HOST`` pointing somewhere that accepts mail. The reversible half
of that -- reading ``EMAIL_HOST``, ``EMAIL_PORT``, ``EMAIL_HOST_USER``,
``EMAIL_HOST_PASSWORD``, ``EMAIL_USE_TLS`` and ``SERVER_EMAIL`` from the uWSGI
environment, written from ``ansible/vars/main.yml`` the way
``KASVIMUSEO_ALLOWED_HOSTS`` is (issue 026) -- was written while this question
was outstanding and is not merged. It is on the tag
``interim-email-wiring-066`` rather than in the history, because carrying
settings nothing reads is the same kind of thing this issue just deleted.

See also
========

:doc:`065 <065-with-debug-off-a-500s-traceback-is-written-nowhere>` -- the
application half, and where the reasoning for keeping the handler at all is
written out. That reasoning is overturned here, and it is worth reading for
what it got right rather than as a mistake: it argued the handler cost nothing
and would start working the day the server could deliver, which was true. What
it could not settle is the question this issue put to the maintainer -- whether
that day was ever going to come. It was not, so the third of its three
arguments, that the handler is the only path to somebody not reading a log
file, turned out to be a path to nobody. 065's own text says the comment gets
rewritten if this issue is acted on, and it has been.
