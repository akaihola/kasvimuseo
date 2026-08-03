====================
What to work on next
====================

Read this page and nothing else to pick up work. It is the ranked order from
:doc:`index` with each issue's current metadata folded in, generated at build
time from the ``:Status:``, ``:Severity:``, ``:Depends on:``, ``:Decision:``
and ``:Claimed:`` fields of ``docs/issues/NNN-*.rst``, so it cannot disagree
with them. The fields themselves are defined in :doc:`README`.

Ready now
=========

Actionable status (``Open`` or ``Accepted``) and nothing unfinished underneath
it, highest-ranked first. Take the top row that is not already claimed.

* **Claimed** names a branch or task that is already doing this. A row with
  something there is not free work: read that branch first, and expect the
  issue's ``Status`` to be ahead of what this page says.
* **Decision** ``needed`` means ``:Decision: undecided`` -- the maintainer has
  not ruled, so the work includes asking. Ask once and carry on: a question is
  not a wait. If no answer has come by the time the rest of the work is done,
  rule on the evidence, record both the question and the ruling in
  ``:Decision:``, and finish. ``ruled`` means the issue file already says what
  to do.
* There is no unmet-dependency column here, because "ready" is defined as
  having none. The issues that have one are in the next table, with the
  dependency and its status named.

.. issue-queue::

Not in the queue
================

Every other issue in the register, and the one reason each is out. Nothing is
silently missing: this table and the one above together list all of them.

.. issue-parked::

Facts for a fresh agent
=======================

Enough to start without reading anything else.

**The integration branch is** ``master``. There is no ``main``. Work on a
branch and rebase it onto ``master``; never merge ``master`` into it.

**The suite** is pytest, and it runs inside the application's container,
because the application is Django 1.5 on Python 2.7::

    $ dev/kasvimuseo app test              # starts and stops PostgreSQL itself

It needs PostgreSQL and nothing else -- no production dump, no media -- and
takes about ten seconds. Run by hand instead of through the script, it wants
``DJANGO_SETTINGS_MODULE=ylaneenkasvit.test_settings`` and a running cluster
(``dev/kasvimuseo db start``); the rest of the configuration is in
``pytest.ini``. The host's Python 3 cannot run it: nothing on the host has
Django 1.5.

**The documentation** builds on the host, outside the container::

    $ dev/kasvimuseo docs                  # -> .dev/docs/html/index.html

It treats warnings as errors, and this page is generated, so a malformed
``:Status:`` or an issue missing from the ranking fails it. ``--clean``
rebuilds from scratch; ``docs serve`` publishes every checkout on the tailnet.
See ``README.rst`` for both.

**A fix updates its issue file in the same pull request** -- ``:Status:`` to
``Fixed``, ``:Decision:`` to what was decided and why, ``:Resolution:`` to the
commit -- and removes ``:Claimed:``. That is what takes it off this page;
there is no separate list to edit. The ranking entry in :doc:`index` stays
where it is, since it records what was decided about the order, not what is
left to do.

**One issue per file, numbers never reused.** New reports land in
:doc:`incoming` in whatever shape they arrive and are split into numbered files
from there.

**Never end a turn waiting for a person.** Nothing here runs attended: an agent
picking this page up may be the only thing awake. Asking the maintainer is
allowed and often right, but the answer may never come, and a turn that ends
waiting for one has not ended -- it has stalled a task nobody is watching. Ask,
then keep working on everything the answer does not decide. Land what you can
and say plainly in the issue file what is still owed and who owes it: an
``Accepted`` issue with a "What is left" section is a finished piece of work,
not an unfinished one. 056 is the shape to copy.

How this page stays honest
==========================

Two directives, both defined in ``docs/_ext/sphinx_issue_register.py``:
``issue-queue`` and ``issue-parked``. They read every ``docs/issues/NNN-*.rst``
and every ``issue-rank`` block in :doc:`index`, and the build fails -- rather
than rendering something out of date -- when

* a ``:Status:``, ``:Severity:`` or other docinfo field is missing, empty,
  duplicated, misspelled or has a value :doc:`README` does not define,
* an issue file is not in the ranking, or is in it twice,
* the ranking names an issue that has no file.

The order itself is the one thing here no script derives: it is a judgement,
argued for in :doc:`index` and written out beside the argument. Everything
else on this page is read from the issue files.
