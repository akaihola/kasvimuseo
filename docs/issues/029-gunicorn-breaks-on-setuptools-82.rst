========================================================
Issue 029: gunicorn <= 20.1.0 breaks on setuptools >= 82
========================================================

:Status: Open
:Severity: Low
:Area: dependencies / build
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Decision: undecided
:Resolution: (none yet)

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

See also
========

``docs/upgrade-plan.rst`` Part 3b.2. Issue 021 is the unrelated cosmetic
gunicorn problem.
