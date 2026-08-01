==============================================
Issue 038: The repository has no rendered docs
==============================================

:Status: Fixed
:Severity: Low
:Area: documentation / tooling
:Reported: 2026-07-28
:Source: Documentation request, branch ``sphinx-docs``
:Evidence: (none)
:Depends on: (none)
:Blocks: (none)
:Related: 018 -- the build moves into CI once one exists
    036 -- each workaround has a stage at which it falls away
    016 -- the ``ur''`` prefix that blocks the parser
:Decision: GitHub Pages, deployed from ``master`` alone, and inert until the
    repository's Pages source is set to "GitHub Actions" by hand. Read the Docs
    was the alternative and was not taken: it would build these documents a
    second way, on its own runner with its own invocation of Sphinx, and the
    value of the CI job is that it runs ``dev/kasvimuseo docs --clean`` -- the
    same command a developer runs, so the two cannot drift. What Read the Docs
    offers over Pages is a rendered preview per pull request; ``dev/docs-serve``
    already renders every unmerged branch, which is the same need answered
    without a second toolchain. Publishing at all was ruled safe because the
    repository is already public: this register names production hostnames, the
    contents of an untracked settings file on the server, and three live
    security issues (049, 050, 051), and every word of it is served by
    github.com today. A rendered site changes how easily that is found, not
    whether it is disclosed -- closing those three issues is what ends the
    disclosure.
:Resolution: (to be filled in with the commit)

Problem
=======

``docs/`` holds three substantial reStructuredText documents -- the upgrade plan,
the dependency inventory and the test coverage plan -- and 38 issue files, and
they are only ever read as source. There is no front page, no index, no
cross-referencing between an issue and the code it is about, and no rendered
form to hand to anyone. The API surface -- ``kasvimuseo`` and
``ylaneenkasvit`` -- is documented nowhere at all.

The obvious answer is Sphinx, and the documents are already reStructuredText.
The obstacle is the runtime: the application is Python 2.7 / Django 1.5 (issue
036), so the code cannot be imported by anything modern, and modern Sphinx
cannot run on Python 2.7. Any documentation build has to sit *outside* the
application runtime until the upgrade catches up with it.

Decision
========

Build the documentation with a **host-side Python 3 toolchain that never
imports the application**, and rebuild it automatically -- in the background,
never blocking -- whenever a coding agent edits documentation or source.

Two conventions in this repository are load-bearing for the design:

* ``.dev/`` is throwaway state, gitignored, safe to delete (see ``README.rst``).
  The rendered HTML belongs there, not in the tree.
* ``dev/kasvimuseo`` is the single documented entry point for development
  commands. The documentation build is one more subcommand.

Design
======

Toolchain
---------

``docs/requirements.txt`` pins ``sphinx``, ``sphinx-autoapi`` and ``furo``, and
every invocation is::

    uv run --no-project --with-requirements docs/requirements.txt sphinx-build ...

``--no-project`` matters: there is no ``pyproject.toml`` here, and the
requirement sets under ``requirements/`` are the Python 2.7 application's, which
``uv`` cannot resolve at all (its floor is Python 3.6). The documentation
toolchain and the application share no environment, no interpreter and no lock
file. That is the whole trick that makes this possible today.

The API index: autoapi, not autodoc
-----------------------------------

``sphinx.ext.autodoc`` imports each module to introspect it. That requires a
working Django 1.5 environment on Python 2.7, i.e. the dev container, where
modern Sphinx cannot run. **sphinx-autoapi** instead parses the source
statically and never executes it, so it works from the host against Python 2-era
code.

Because the descriptions are read off the syntax tree rather than off live
objects, every entry links to its own source through ``sphinx.ext.viewcode``.
That extension has to be listed **before** ``autoapi.extension`` in
``conf.py``: in the other order autoapi never hands it the parsed source, the
``[source]`` links quietly do not appear, and nothing warns.

One file cannot be parsed by a Python 3 tokeniser at all:
``kasvimuseo/migrations/0011_extract_lighting.py`` uses the Python 2 ``ur''``
string prefix. Migrations are excluded from the API index regardless -- 19
South migrations are noise in an API reference -- so the exclusion is not a
workaround borrowed for the occasion.

Layout
------

``docs/`` is the Sphinx source directory; the existing documents stay where they
are and are wired into the tree rather than moved.

============================ =========================================
``docs/conf.py``             new
``docs/index.rst``           new -- front page, project description
``docs/issues/index.rst``    new -- issue list, glob toctree
``docs/requirements.txt``    new -- pinned doc toolchain
``docs/issues/*.rst``        existing, unchanged
``docs/*-plan.rst`` etc.     existing, unchanged
============================ =========================================

The issue list uses a ``:glob:`` toctree over ``0*``, so a new issue file appears
in the rendered list with no edit anywhere else. The API pages are generated
under ``/api/`` from ``kasvimuseo`` and ``ylaneenkasvit``, ignoring migrations
and tests.

Output goes to ``.dev/docs/html/``, doctrees to ``.dev/docs/doctrees/``.

Automatic rebuild that does not block the agent
-----------------------------------------------

``dev/docs-build`` runs the build under ``flock -n``, so overlapping invocations
collapse into one instead of stacking, and logs to ``.dev/docs/build.log``.

``dev/docs-hook`` is what a ``PostToolUse`` hook calls. It reads the hook JSON on
standard input and exits immediately unless the edited path is documentation or
Python source; for one that is, it runs the build. The hook is registered with
``"async": true``, which is the harness's own mechanism for a hook that must not
hold up the agent -- and, unlike detaching the build inside the script, it
leaves the process owned by something that will not reap it.

The hook resolves the repository root from the *edited file*, not from the
agent's working directory, so edits made in a ``git worktree`` rebuild that
worktree's documentation rather than the base checkout's.

One thing measured while building this: **a sandboxed agent environment kills a
detached process when the call that spawned it ends.** The first version of the
hook used ``setsid nohup``, and in the sandbox used here that build died
part-way through, every time -- which is what pointed at ``"async": true`` as
the right mechanism instead.

Nothing is lost when a build is killed -- Sphinx keeps its doctrees, so the next
one costs about six seconds against the twelve a full build takes (and the
forty of the very first run, which also downloads the toolchain) -- but the
documentation would silently stay stale. ``dev/docs-build`` therefore leaves a
``.dev/docs/.incomplete`` marker for the duration of a build and clears it only
on success, and the hook treats that marker as reason enough to build again,
whatever was edited. The docs catch up on the next edit instead of waiting for
someone to notice.

Serving it
----------

``dev/docs-serve`` (``dev/kasvimuseo docs serve``) serves every checkout at
once: the main one and each ``git worktree``, each from its own
``.dev/docs/html/``, under ``/<branch>/``, with an index at ``/`` and a switcher
injected into each page that moves to the same path in another checkout. The
main checkout also answers at ``/main/``, because its branch changes underneath
a bookmark. The checkout list comes from ``git worktree list`` on every request,
so worktrees appearing and disappearing need no restart.

It binds to the machine's Tailscale address when ``tailscale ip -4`` answers,
which keeps the docs on the tailnet rather than on every interface; ``--bind``
overrides it and ``0.0.0.0`` is the fallback. It is stdlib Python 3 -- no part
of the Sphinx toolchain is needed to *read* the docs, only to build them --
and it never writes: the injected switcher exists only in the response, never in
the built HTML.

Per-checkout builds are the point. Each worktree renders its own branch, so a
documentation change can be read as it will look before it is merged, from a
phone or another machine, without touching the main checkout.

A warning is a failure
----------------------

The build runs with ``-W``, so a malformed page, a broken cross-reference or a
document nobody linked to makes it exit non-zero. Sphinx 9 keeps going after a
warning rather than stopping at the first, so the HTML is still written: the
docs stay current *and* the problem is reported. ``dev/docs-hook`` throws away
standard output and lets standard error through, which means a rebuild that
went fine says nothing at all and a rebuild that did not names the file and the
line.

This is worth the strictness only because the tree is genuinely warning-free,
and getting there took one targeted exclusion. ``models.py`` defines
``get_next_observation_extid`` and then rebinds the name to
``lazy(get_next_observation_extid, unicode)``, so autoapi documented a function
and a module attribute under one name and warned about the duplicate. An
``autoapi-skip-member`` handler in ``conf.py`` drops the attribute and keeps the
function. That is the only thing silenced by name; everything else that warns is
meant to be fixed.

One trap comes with this. **An incremental build only re-reads changed files, so
warnings from everything else are not re-emitted** -- a page can be broken and
quiet until something touches it again. ``dev/kasvimuseo docs --clean`` reads
the whole tree, and is what to run before believing a clean build. This is how
the malformed title of issue 042 went unnoticed for a day.

Migration to modern practice, as the stack catches up
=====================================================

Everything above is shaped by a Python 2.7 application, and each constraint has
a defined point in ``docs/upgrade-plan.rst`` at which it stops applying. The
documentation build should be revisited at these points rather than left to
ossify.

======================= ================================================================
Trigger                 Change
======================= ================================================================
Stage 10 (Python 3.7)   Application becomes importable by a modern interpreter.
                        Replace sphinx-autoapi with ``sphinx.ext.autodoc`` +
                        ``autosummary``, which reads real signatures, decorators and
                        inherited members instead of an AST approximation. Requires a
                        Django settings module and ``django.setup()`` in ``conf.py``.
                        Keep autoapi until this stage: it is the only option that works.
Stage 10                Drop the ``0011_extract_lighting.py`` parse exclusion note; the
                        ``ur''`` prefix is gone by then (issue 016 territory).
Stage 10                ``uv`` can finally resolve the application itself. Replace
                        ``docs/requirements.txt`` with a ``pyproject.toml``
                        ``[dependency-groups] docs = [...]`` entry, built with
                        ``uv run --group docs``, and a real ``uv.lock`` -- one
                        environment definition instead of two.
Stage 10                Add ``sphinx.ext.intersphinx`` against the Python and Django
                        object inventories, pinned to the version actually in use, so
                        ``ForeignKey`` and ``QuerySet`` in docstrings become links.
                        Pointless before then: docs.djangoproject.com no longer
                        publishes an inventory for 1.5.
Stage 11+ (Django 2.0)  Consider ``sphinxcontrib-django`` for model field tables in the
                        API reference. It requires Django >= 2.
CI exists (issue 018)   **Done, with this issue.** ``dev/kasvimuseo docs
                        --clean`` runs on every pull request and every push to
                        ``master``; a ``pages`` job publishes the HTML from
                        ``master`` alone, so a pull request builds and fails on
                        a warning without deploying anything. ``-W`` was already
                        on locally. The hook is still the fast local loop, and
                        ``dev/docs-serve`` still shows unmerged branches, which
                        the published site cannot. One switch is not in the
                        repository: see "Not done here".
Any time                ``sphinx-autobuild`` would give ``dev/docs-serve`` live reload
                        and rebuild-on-change in one process. It is a dependency and a
                        different design -- one checkout per process -- so it is worth
                        it only if the hook turns out not to be enough.
Any time                If the docs server should survive a logout, it is a systemd
                        user unit, not a change to the script. Deliberately left out:
                        a foreground process that dies with the terminal is the
                        expected behaviour of a development tool.
Any time after CI       Turn on ``sphinx.ext.doctest`` and ``coverage`` builders, so
                        examples in the documentation are executed and undocumented
                        public API is reported.
Any time                If Markdown becomes preferable for new documents, add ``myst``
                        rather than converting the existing reStructuredText. The two
                        coexist in one project.
======================= ================================================================

With that row done, nothing left in this table is waiting on this issue. Every
remaining trigger is either a stage of ``docs/upgrade-plan.rst`` that has not
been reached -- Stage 10 for the four workarounds above, Stage 11 for the model
field tables -- or an "Any time" row that is a standing option rather than
outstanding work, including the ``doctest`` and ``coverage`` builders that CI
existing has now made possible. That is scheduled, not forgotten: this issue is
``Fixed`` because the design landed and CI now enforces it, not because the
table is empty.

One thing measured while wiring the build into CI, and worth writing down
because it cuts against the row above: ``--clean`` catches nothing on a hosted
runner *today*. Every run starts from a fresh checkout, so there are no
doctrees to be incremental against and the build was already reading the whole
tree. What the flag does is state the property the job depends on, so that
caching ``.dev/docs`` to save twenty-five seconds cannot quietly turn the check
into a rubber stamp. The property itself was verified rather than assumed: a
deliberate broken cross-reference in a page the branch did not otherwise touch
turned the job red.

Two things deliberately do **not** change with the stack. The output stays in
``.dev/`` and out of version control -- rendered HTML in a diff is noise. And
the rebuild stays detached and non-blocking; a documentation build is never
worth making an agent wait.

Not done here
=============

The ``PostToolUse`` hook has to be registered in ``.claude/settings.json``, which
coding agents cannot write to. The scripts are in the repository and work when
run by hand; the registration is a one-line manual step, recorded in
``README.rst``.

The published site needs the same kind of step, for the same reason. A workflow
cannot switch GitHub Pages on for its own repository, so until somebody sets
**Settings -> Pages -> Source** to "GitHub Actions" there is nowhere to deploy
to. The ``pages`` job asks the API whether a Pages site exists and skips the
deployment with a notice when it does not, so master stays green rather than
going red over a switch nobody has flipped; the moment it is flipped, the next
push to ``master`` publishes, with no change to the workflow. The site is
``https://akaihola.github.io/kasvimuseo/``, and it is in ``README.rst``.
``actions/configure-pages`` can enable Pages itself with ``enablement: true``,
which was deliberately not used: whether these documents are published is the
maintainer's decision and not a side effect of a build.

Sphinx deletes no page whose source has gone, so renaming a document leaves its
old HTML in ``.dev/docs/html/`` -- reachable by URL and by nothing else, since
no index links to it. Rather than teach the build which outputs belong to which
sources, ``dev/kasvimuseo docs --clean`` throws the output away and rebuilds,
which costs thirteen seconds. This happened for real once already, when issue
037 became 038 mid-review.

Two limits worth knowing about the automatic rebuild. It is driven by the
harness's ``Write|Edit|MultiEdit`` events, so a file changed by ``sed`` in a
shell, by ``git checkout``, or by a human in an editor does not trigger it --
``dev/kasvimuseo docs`` does. And the hook watches ``docs/``, ``kasvimuseo/``,
``ylaneenkasvit/`` and ``README.rst`` by name: a new top-level package would
need adding to that list in ``dev/docs-hook``.
