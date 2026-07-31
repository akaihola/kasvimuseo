========================================================
Issue 029: gunicorn <= 20.1.0 breaks on setuptools >= 82
========================================================

:Status: Fixed
:Severity: Low
:Area: dependencies / build
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: (none)
:Blocks: 027 -- a constraint the lock must carry
    036 -- Stage 10 onwards
:Related: 021 -- the unrelated cosmetic gunicorn problem
:Decision: Take the option: gunicorn goes 0.17.4 -> **21.2.0** at the Python 3
    flip (upgrade plan Stage 10), skipping 19.x and 20.x, and **no stage
    carries a** ``setuptools<82`` **bound**. Nothing is pinned differently
    today; the pin is 0.17.4 either way until Stage 10. Recorded beside the
    ``gunicorn`` pin in ``requirements/production.txt``, which is the only
    place the version is set, and in ``docs/upgrade-plan.rst`` 3b.2 and
    Stage 10.
:Resolution: 679d96d -- the ruling, beside the gunicorn pin and in
    Stage 10 of the upgrade plan. No version changed

Problem
=======

gunicorn imported ``pkg_resources`` until 21.2.0, and setuptools stopped
shipping ``pkg_resources`` in 82.0.0.

Grepping the shipped packages:

=================== ==============================================
gunicorn            imports ``pkg_resources`` in
=================== ==============================================
19.10.0             ``util.py``, ``app/pasterapp.py``
20.1.0              ``util.py``, ``workers/ggevent.py``,
                    ``workers/geventlet.py``
**21.2.0** ...      nothing
=================== ==============================================

=================== ==============================================
setuptools          ships ``pkg_resources/``
=================== ==============================================
... 81.0.0          yes
**82.0.0** ...      **no**
=================== ==============================================

Resolving the middle upgrade stages without constraints selects
``gunicorn==20.1.0`` together with ``setuptools==82.0.1`` -- a gunicorn that
cannot import, in a combination nothing warns about.

Impact
======

Low, because the fix is free and permanent. It is filed separately from issue
027 only because the remedy is a decision about gunicorn rather than about
pinning discipline.

Options
=======

**Go straight to gunicorn 21.2.0 at the Python 3 flip** (upgrade plan Stage
10), skipping 19.x and 20.x entirely. gunicorn 21.2.0 requires only
Python >= 3.5 and is completely independent of Django, so nothing else
constrains the choice. Sitting on gunicorn 20 buys nothing and costs a
``setuptools<82`` constraint carried through eight stages.

Until then the current pin, 0.17.4, is unaffected -- it runs on Python 2.7,
where setuptools 82 does not exist.

What was recorded, and where
============================

This one changes no pin at all -- the decision is about a version this project
has not reached yet -- so the whole of it is a sentence in two places:

``requirements/production.txt``
    Beside ``gunicorn==0.17.4``, the only place the version is set. It says
    why this pin is unaffected and what replaces it, so that whoever raises it
    does not land on 20.1.0 by walking the ladder one rung at a time.

``docs/upgrade-plan.rst``
    3b.2 and Stage 10 now say the ruling was taken, and that no stage carries
    a ``setuptools<82`` bound as a result.

Issue 044 does not change it
============================

``dev/kasvimuseo app run`` serves the development site through gunicorn rather
than ``manage.py runserver`` -- that is issue 044's fix, and it made gunicorn a
development dependency as well as a production one. Checked rather than
assumed: the script runs the ``gunicorn`` executable inside the same image,
against the same ``requirements/production.txt`` pin and the same Python 2.7,
so it is exposed exactly when production is, which is not at all. There is no
second version of gunicorn anywhere to constrain. It does mean the Stage 10
move is felt by developers on the day it happens, which is an argument for
making it once and early rather than in two steps.

Not touched: ``INSTALLED_APPS``. The ``'gunicorn'`` entry there is issue 021,
a different problem that may be in flight elsewhere.

What 027 has to carry
=====================

Nothing, which is the point of deciding it this way. Had gunicorn 20.1.0 been
chosen for Stages 10-17, every one of their locks would have had to pin
``setuptools<82`` -- a bound on a build tool that no requirements file
currently mentions, for a reason invisible in any package's metadata. Instead
each lock from Stage 10 on names ``gunicorn==21.2.0`` and says nothing about
setuptools. The ceiling below Stage 10 is the interpreter: gunicorn 0.17.4 on
Python 2.7, where setuptools 82 cannot be installed.

See also
========

``docs/upgrade-plan.rst`` Part 3b.2. Issue 021 is the unrelated cosmetic
gunicorn problem.
