=================
Your first change
=================

For somebody who has not worked on this project before, and wants to land one
change without reading everything first. It is the sequence, not the reference:
each step says what to do and where the full account of it lives.

If you already know the project, :doc:`issues/next` is the page you want
instead. This one exists because that page assumes the sequence below.

The words this project uses
===========================

Four, and they are worth two minutes because every other page assumes them.

**The register**
    ``docs/issues/``: one file per known problem, numbered, each carrying a
    ``Status`` field that is the thing actually tracked. Not a bug tracker
    somewhere else -- it is in the repository, so a fix and the record of the
    fix land in the same commit. :doc:`issues/README` defines every field.

**The queue**
    :doc:`issues/next`, generated from those files each time the documentation
    builds. It is the ranked list of what can be started today. Nobody edits
    it; changing an issue's ``Status`` is what moves it.

**Claimed**
    A field naming the branch that has an issue in hand. It is how you avoid
    starting something somebody else is already doing, and it is deleted by the
    change that resolves the issue.

**A stage**
    One step of a plan -- :doc:`upgrade-plan` has twenty, and
    :doc:`test-coverage-plan`'s packages are all done. Stages are not issues:
    the plan already argued for the order, so there is nothing to rank. "Where
    this plan has got to", at the top of each plan, says which one is next.

Set the project up
==================

The application is Django 1.5 on Python 2.7, so it runs in a container with a
throwaway PostgreSQL cluster beside it, and one script drives all of it. You
need ``podman`` and a PostgreSQL installation. :doc:`development` is the full
account, including how to get a database with data in it; the shortest path
that gets you a running application is at the top of it.

You do not need the production dump to write code or run the suite. You do need
it to look at real data.

Pick something to work on
=========================

Read :doc:`issues/next` and take the top row of "Ready now" that has nothing in
its **Claimed** column. That is the whole selection procedure: the ranking
argument is in :doc:`issues/index` if you want it, but the queue has already
applied it.

Two columns decide how much work the row is. **Decision** ``needed`` means the
maintainer has not ruled on what the fix should be, so the work includes asking
-- ask, and carry on rather than waiting. **Severity** is user-visible impact,
not difficulty.

If the queue is empty of anything you can do, the next stage of
:doc:`upgrade-plan` is the other source of work.

Make the change
===============

Cut a branch, and say so in the issue file straight away::

    :Claimed: branch ``feature/short-name``

That line on ``master`` is what stops two people doing the same work; a status
you only set on your own branch is invisible to everybody else.

Then write the change and its test. The suite is the safety net for everything
else here, so a change without one is unusual enough to need a sentence saying
why in the issue file.

Check it
========

Two commands, and both of them are what CI runs::

    $ dev/kasvimuseo app test      # pytest, in the container, about 20 seconds
    $ dev/kasvimuseo docs          # Sphinx, on the host, warnings are errors

The suite has a coverage floor, so a change that adds code without tests can
fail on the number rather than on a test. The documentation build fails on a
malformed issue field, on a ranking that does not list every issue exactly
once, and on a commit that a ``Resolution`` names but the repository does not
have; the message says which. :doc:`issues/README` explains each check.

The browser suite, ``dev/kasvimuseo app browser-test``, is only needed if you
touched the label editor.

Land it
=======

**The issue file is part of the change, in the same commit.** Set ``Status`` to
``Fixed``, put the commit in ``Resolution``, write what was decided and why in
``Decision``, and delete ``Claimed``. That is what takes the issue off the
queue: there is no separate list to update.

One catch worth knowing before it bites you: write the ``Resolution`` commit
**after** the branch has landed on ``master``. Rebasing rewrites your commits,
so a hash written before the rebase points at a commit that no longer exists.
The documentation build now catches that, which is the only reason it is a
footnote rather than a trap.

Branch onto ``master`` and rebase; never merge ``master`` into your branch.
There is no ``main`` in this repository.

Found something else on the way?
================================

Write it in ``docs/issues/incoming.rst`` in whatever shape it arrives -- a
sentence is enough. Somebody, possibly you, turns it into a numbered file
later. Do not fix it in passing in the same branch: an unrelated fix in a
change is the thing that makes a review hard.
