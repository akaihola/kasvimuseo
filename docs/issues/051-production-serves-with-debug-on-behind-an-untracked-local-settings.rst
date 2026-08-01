==================================================================
Issue 051: Production serves with DEBUG on, from an untracked file
==================================================================

:Status: Open
:Severity: High
:Area: deployment / security
:Reported: 2026-07-31
:Source: Maintainer, reading the server while settling 026
:Evidence: (none) -- the file is on the server and in no checkout; nothing this
    repository can run observes it
:Depends on: 026 -- turning ``DEBUG`` off leaves ``ALLOWED_HOSTS`` in force, and
    the deployment only supplies it because of 026, which is ``Fixed``
:Blocks: (none)
:Related: 049 -- the same deploy can carry both, and its output shows the same
    thing: the server's ``uwsgi.ini`` predates 025
    025 -- where this split between a repository half and a server half started
    050 -- the other server-side act still outstanding
:Decision: undecided -- not whether to do it, which follows from what it is, but
    when and in what order. The order is fixed: the deploy that sets
    ``ALLOWED_HOSTS`` (026) has to be in place before the file goes, or the site
    answers 400 to everything. The timing is the maintainer's, as 049's is.
:Resolution: (none yet)

Problem
=======

The production application runs with ``DEBUG = True``. It is not set anywhere
in this repository and not by Ansible: it comes from a hand-placed, untracked
file on the server, read on 2026-07-31 at
``/home/kasvimuseo/.local/lib/python2.7/site-packages/ylaneenkasvit/local_settings.py``,
whose entire content is::

    import os


    def modify(settings):
        settings['DEBUG'] = True
        settings['TEMPLATE_DEBUG'] = True

``ylaneenkasvit_settings.py`` ends with ``try: from local_settings import *``
and calls ``modify(globals())``, so that file is the last word on the settings
of the running site.

With ``DEBUG`` on, Django 1.5 renders its yellow debug page on any unhandled
exception: the full traceback, local variables in every frame, every executed
SQL statement, and the settings module with values shown for everything it does
not recognise as a secret. It also keeps every query of every request in memory
for the life of the process, which for a long-running uWSGI worker is a slow
leak.

This is the case (2) that :doc:`026
<026-allowed_hosts-is-set-nowhere-in-tracked-settings>` described as the
alternative, and it turned out to be reached by case (1)'s mechanism: an
untracked file is both why the site answers at all and why it answers with
``DEBUG`` on.

Impact
======

Live information disclosure, on a public site, on any error page. What leaks is
whatever is in scope at the point of the exception -- and 049 is still open, so
the ``SECRET_KEY`` visible there is one an unknown number of clone-holders
already have.

Second, and separately: until 026's change is deployed, the site's ability to
serve a request at all depends on that untracked file. It sits in a
``site-packages`` directory that ``ansible-playbook -t code`` writes to with
``pip install --upgrade``. If a deploy ever removes it, every request becomes a
400 with no explanation in this repository.

What to do
==========

In this order, in one maintenance window:

#. Deploy 026's change, so ``uwsgi.ini`` carries ``KASVIMUSEO_ALLOWED_HOSTS``.
   This is the same playbook run 049 needs, and running the ``uwsgi`` tag is not
   optional: the installed code after ``-t code`` refuses to start without the
   environment that ``-t uwsgi`` writes.
#. Delete
   ``/home/kasvimuseo/.local/lib/python2.7/site-packages/ylaneenkasvit/local_settings.py``.
#. Restart uWSGI and check both halves: an ordinary page still renders, and a
   deliberately bad ``Host`` header gets a 400 rather than a page.

When this was filed, nothing in this repository needed to change for it, and
the section below is the one thing that did. If it turns out the file was there
for something other than ``DEBUG`` -- it is not, on the copy above, but the next
person to find one should assume less -- whatever that was belongs in the
tracked settings, which is the lesson 026 already drew.

The playbook that does it exists now
====================================

Those three steps are ``ansible/secure-production.yaml``, in that order, with
the runbook in ``README.rst`` under "The security maintenance window". Three
things about it are this issue's:

* The ordering is not left to whoever is typing. The deletion is guarded by a
  check that reads the server -- that ``uwsgi.ini`` already carries
  ``KASVIMUSEO_ALLOWED_HOSTS``, and that the installed ``common_settings.py``
  is one that reads the environment at all. Running the deletion's tag on a
  server that has not had the deploy fails on that check, names this issue and
  changes nothing. The failure mode described above is therefore not reachable
  by choosing one tag rather than another, which is what it used to be.
* It deletes the bytecode as well as the source. On Python 2 a
  ``local_settings.pyc`` with no ``.py`` beside it is still importable, so
  removing only the file this issue names would leave ``DEBUG`` on and look
  like it had not.
* It checks step 3 rather than describing it: a separate, read-only play
  asserts that an ordinary page answers 200, that a request carrying a host
  name the site does not answer to gets a 400 and that the 400 is not Django's
  debug page, and that neither the file nor its bytecode is left behind. It can
  be run on its own afterwards with ``-t verify``.

Nothing about the state of the server has changed, and ``Status`` says so. The
site still serves with ``DEBUG`` on until the window is run, and when to run it
is the timing this issue's ``Decision`` field leaves to the maintainer.

See also
========

:doc:`026 <026-allowed_hosts-is-set-nowhere-in-tracked-settings>` -- the
repository half, and the reason this can be done at all.
:doc:`049 <049-production-still-runs-the-old-secret-key-and-database-password>`
-- the other half of the same deploy.
