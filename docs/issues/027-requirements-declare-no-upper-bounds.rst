==========================================================================
Issue 027: Requirements declare no upper bounds; --no-deps is load-bearing
==========================================================================

:Status: Open
:Severity: High
:Area: dependencies / build
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none -- reproduce with ``uv pip compile`` on any stage's direct pins)
:Depends on: 028, 029, 030 -- the lock has to record their constraints, so settle them first
:Blocks: 036 -- every upgrade stage needs a complete, reproducible lock
:Related: (none)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

The requirements files pin direct dependencies exactly but say nothing about
their transitive ones, and the packages this project depends on declare only
**lower** bounds. photologue says ``Pillow>=6.0.0`` meaning "6.0 or the few
releases after it"; a resolver reads it as "anything from 6.0 onwards" and
picks Pillow 12.

Resolving the project's own direct pins with ``uv pip compile`` demonstrates
this. Asking for Django 2.2 with photologue 3.10 -- a 2019 combination --
selects ``pillow==11.3.0``, ``exifread==3.5.1`` and ``setuptools==82.0.1``,
none of which existed when photologue 3.10 was written, and two of which break
it (issues 028 and 029).

The project already works around this. ``dev/Containerfile`` does::

    # --no-deps keeps the pinned versions exactly as listed (see fabfile.py: it also
    # avoids photologue dragging in an incompatible Pillow).
    RUN pip install --no-cache-dir --no-deps -r /tmp/production.txt \
     && pip install --no-cache-dir 'Pillow==6.2.2' 'django-sortedm2m==1.5.0'

That comment is correct and the workaround is load-bearing, but it is invisible
to anyone reading ``production.txt``, and it means the *real* dependency set is
split across two files with two different mechanisms. ``Pillow`` and
``django-sortedm2m`` are genuine runtime dependencies that ``production.txt``
does not mention.

Impact
======

Today: an incomplete and slightly misleading picture of what the application
actually needs. ``setup.py`` reads ``production.txt`` into ``install_requires``,
so anyone installing the package the normal way gets neither Pillow nor
sortedm2m, and photologue fails at import.

During the upgrade: this is the mechanism by which several stages will silently
select incompatible transitive versions. Each stage's pin set has to be a
complete lock or the stage is not reproducible.

Options
=======

Adopt ``uv pip compile``: keep a short ``requirements/production.in`` with the
direct pins and the necessary upper bounds, and commit the generated,
fully-pinned ``requirements/production.txt``. ``--no-deps`` then becomes
unnecessary, because the file already names every package and version.

``docs/upgrade-plan.rst`` Appendix A contains the resolved lock for every stage
from 10 onwards, produced this way. Stages 0-9 are on Python 2.7, which ``uv``
cannot target, so those stay hand-maintained.

See also
========

Issues 028, 029 and 030 are the three concrete breakages this class of problem
produces. ``docs/upgrade-plan.rst`` Part 3b.
