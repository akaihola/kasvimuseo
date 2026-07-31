==========================================================================
Issue 027: Requirements declare no upper bounds; --no-deps is load-bearing
==========================================================================

:Status: Fixed
:Severity: High
:Area: dependencies / build
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none -- reproduce with ``uv pip compile`` on any stage's direct pins)
:Depends on: 028, 029, 030 -- the lock has to record their constraints, so settle them first
:Blocks: 036 -- every upgrade stage needs a complete, reproducible lock
:Related: (none)
:Decision: Complete ``requirements/production.txt`` by hand and defer the
    ``.in`` / ``uv pip compile`` half to the Python 3 flip. The file now names
    every runtime package at an exact version -- ``Pillow==6.2.2`` added, with
    028's bound beside it -- so ``dev/Containerfile`` installs one file with
    one command and the second ``pip install`` is gone. ``--no-deps`` stays,
    measured to be a no-op, as the guard that keeps an unpinned package out.
    ``django-sortedm2m`` is **not** added: photologue 2.6.1 does not use it
    (see below), so it left the image with the workaround that put it there.
    The two-file scheme starts at Stage 10, where ``uv`` can run and Appendix A
    already has the generated locks. Recorded in ``requirements/production.txt``
    (the header says the file *is* the Stage 0 lock and why it is
    hand-maintained), in ``dev/Containerfile`` and the production
    ``Dockerfile``, and in ``docs/upgrade-plan.rst`` Part 3b, Stage 2 and
    Appendix A
:Resolution: 5e98596 -- completes the file, deletes the second install
    and the sortedm2m pin, and records the ruling in the upgrade plan

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

What was measured before deciding
=================================

Three things, none of them assumed.

**``uv`` refuses this interpreter, and its nearest answer is wrong.** Run on
today's pin set::

    $ uv pip compile --python-version 2.7 requirements/production.txt
    error: Invalid version request: Python <3.6 is not supported but 2.7 was
    requested.

Asked for 3.7 instead it resolves in seven seconds and produces exactly the
nine direct pins plus ``pillow==9.5.0`` -- the correct Pillow for Stage 10 and
one that does not install on Python 2.7 at all. So a ``production.in`` today
would be an input file with no compiler: nothing could regenerate the ``.txt``
from it, and anyone who tried would get a lock that cannot be built. That is
the whole argument for deferring the mechanism rather than the completeness.

**The transitive closure is one package, not a long tail.** ``pip freeze`` in
the built image, minus the test stack, and then the ``dist-info`` of everything
in it. Only two packages in the set declare anything: photologue 2.6.1 wants
``Django>=1.4``, ``South>=0.7.5`` and ``Pillow>=2.0.0``, and django-extensions
wants ``six>=1.2``. Three of those four are already pinned in the file. Adding
``Pillow==6.2.2`` therefore does not begin a lock -- it finishes one. Measured
from the other end as well: with Pillow in the file, ``pip install -r
production.txt`` *without* ``--no-deps`` installs the same ten packages, which
is why ``--no-deps`` could be dropped and why keeping it costs nothing.

**``django-sortedm2m`` is not a dependency of this photologue.** The issue
above says it is, and so did the comment in ``dev/Containerfile``; both were
wrong, and ``docs/upgrade-plan.rst`` Part 2.1 had suspected as much in a
sentence nobody had acted on. photologue 2.6.1 does not declare it, ``grep -rl
sortedm2m`` finds nothing anywhere under the installed ``photologue/``, nothing
in this repository imports it, and it is not in ``INSTALLED_APPS``. ``uv``'s
resolution does not include it either. It becomes real at photologue 2.8 --
upgrade plan Stage 2, which needs 1.1.1 or later without declaring it; the
declaration first appears at photologue 3.4. Built without it, the suite is
406 passed and the browser suite 11 passed.

Putting it in ``production.txt`` would have been the same defect this issue is
about, pointing the other way: a file that does not say what the application
needs. So it is out of the image, and ``production.txt`` carries a comment
saying it is deliberately absent, why, and when it arrives.

What ``setup.py`` declares now
==============================

``install_requires=[line for line in open('requirements/production.txt')]``
was checked rather than reasoned about: ``python setup.py egg_info`` inside the
container writes a ``requires.txt`` containing the pins and nothing else, so
setuptools does silently drop the comment lines, including the long ones this
file has grown. The ``django-jqm @ <url>`` line survives as a PEP 508 direct
reference, which ``pip install`` of this package honours -- issue 031 is what
to do about the URL itself, and this change does not touch it.

It is honest after the change. Before it, a plain ``pip install`` of this
package produced an environment with no Pillow, where importing photologue
fails; now it declares all ten runtime packages, because the file it reads is
the whole set.

What 030's record cost
======================

Issue 030 asked for its constraint to be recorded "beside
``django-sortedm2m==1.5.0`` in ``dev/Containerfile``, the only place the
version is set", and this change removes that pin. The record moves rather than
disappearing: ``production.txt``'s comment on the package's absence names the
``setuptools<60`` build bound and says the version to reach for is in Appendix
A, and ``docs/upgrade-plan.rst`` 3b.3 says the same at length. 030's ruling is
untouched and its ``Status`` is unchanged -- the constraint was always on the
machine doing the build rather than on anything a lock can pin, which is why
losing the pin loses nothing.

What 036 may now assume
=======================

Stage 0's requirements file is a complete lock: ten packages, all exact, no
second install anywhere, and the ``--no-deps`` that guards it. A stage can
therefore be described by editing one file, and an omission shows up as an
``ImportError`` in the image rather than as an unpinned package nobody chose.
What 036 may **not** assume before Stage 10 is a *generated* lock: Stages 0-9
stay hand-maintained, as ``docs/upgrade-plan.rst`` Appendix A already said, and
no ``*.in`` file exists for them. From Stage 10 the ``.in`` / ``uv pip
compile`` pair is what Appendix A's sets become.

See also
========

Issues 028, 029 and 030 are the three concrete breakages this class of problem
produces. ``docs/upgrade-plan.rst`` Part 3b.
