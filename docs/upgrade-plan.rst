=========================================================
 Dependency and platform upgrade plan: Django 1.5 → 6.0
=========================================================

:Date: 2026-07-28
:Scope: every Python dependency of ``ylaneenkasvit``/``kasvimuseo``, the
        Python runtime itself, and the code changes each step forces

.. contents::
   :depth: 2
   :local:


Where this plan has got to
==========================

Generated from the ``:Status:`` field under each stage heading in Part 4, so
it cannot disagree with them. ``Next`` is the stage to do now: everything above
it is done and names the commit that landed it, everything below it is waiting.
There is no separate list to keep in step -- a stage that lands changes its own
field, and this table follows.

.. stage-queue:: upgrade-plan.rst

The reasoning for each stage, and what it cost when it ran, is in the stage's
own section. The ordering constraints that produced this sequence are in Part 2
and Part 3b.


How this was produced
=====================

Everything below is derived from primary sources, not from recollection:

* PyPI JSON metadata for every package in the tree — each release, its
  ``requires_python``, its ``requires_dist`` and its ``Framework :: Django ::``
  classifiers — 2371 release records across 49 packages. The full listing is in
  ``dependency-inventory.rst`` next to this file; it covers every package in all
  four requirements files, including the Python 2 backports.
* The **source tarballs** of 20 Django releases (1.5.12 … 6.0.7), extracted and
  grepped for the exact modules, functions and settings this project uses. The
  "removed in" columns in `Django API removals`_ are observations of what is
  and is not in the shipped code, not documentation claims.
* The source tarballs of django-photologue (2.6.1 … 3.20), django-grappelli
  (2.4.5 … 5.0.0), django-sortedm2m, pytest-django and django-extensions —
  their ``CHANGELOG``, ``README`` and ``tox.ini`` files, which state
  Django support far more accurately than their (frequently stale) PyPI
  classifiers.
* **``uv pip compile``**, run once per stage, to check that each stage's pin set
  actually resolves and to obtain its full transitive closure. This turned up
  three breakages that metadata alone does not reveal — see
  `Part 3b — Cross-package breakages`_. The resulting lock sets are in
  `Appendix A — Resolved lock set per stage`_.
* **Real installations of the Stage 18 and Stage 19 targets**, verified with
  ``pipdeptree`` and a Django ``check`` run — see
  `The destination is verified`_.

Three limits are worth stating up front, because they bound how much of this is
verified rather than reasoned:

#. ``uv`` refuses to target Python below 3.6, so **no Python 2.7 stage could be
   resolved with it**. Stages 0–9 rest on PyPI metadata and changelogs alone.
#. No interpreter older than 3.14 was available, so the resolutions for
   Stages 10–18 use the correct *environment markers* for their target Python
   but were evaluated with a modern build backend. Where that distinction
   matters (3b.3) it is called out.
#. ``podman`` was not usable in this environment, so **the project's own
   container was never built or run**. Nothing here was tested against the
   actual application code or a real database — no migration was executed, no
   page was rendered. Stages 18 and 19 were verified as *dependency stacks*
   (see below), not as this project running.

In short: the constraints between packages are verified; the interaction between
those packages and this project's own code is analysed from its source but not
executed. The first stage to run should be treated as a test of that reasoning.

Where a compatibility claim could **not** be verified from a primary source it
is marked "unverified" rather than asserted.


Where the findings live
-----------------------

This document is the *reasoning*: the constraints, the ordering they force, and
the evidence behind both. Everything actionable that came out of it is filed
separately under ``docs/issues/``, one document per finding, each with a
``Status`` and ``Decision`` field so the decisions can be tracked.
``docs/issues/README.rst`` indexes them and explains the convention.

Issues **019-036** came from this work. ``docs/issues/036`` is the umbrella for
the modernisation itself and points at the rest; start there. The mapping back
into this document:

=================== ===========================================================
Issue               Analysed in
=================== ===========================================================
019, 023            Part 3, the two settings landmines
024                 Part 3, Python 2 → 3 code work
025, 026            Part 6
027, 028, 029, 030  Part 3b, and Appendix A for the resulting locks
020, 021, 022,      Part 5, packages and configuration that stop being needed
031, 032, 033
034                 Part 6, "The admin-list fork is deleted in Stage 5",
                    and Stage 5 itself
035                 Parts 2.2 and 2.3, the grappelli and photologue ladders
036                 Part 4, the whole staged sequence
=================== ===========================================================

Issue ``016``, filed by the test coverage work, is the other Python 3 landmine
and was a prerequisite of Stage 10. It is ``Fixed``: ``remove_diacritics``
joins rather than filters, so Stage 10 has nothing to do there.


The destination is verified
---------------------------

.. _`The destination is verified`:

The far end of this plan is not a projection. **Two stages were installed and
run for real**: Stage 19 (Django 6.0.7, grappelli 5.0.0, photologue 3.20) and
Stage 18 (Django 5.2.16, grappelli 4.0.4, photologue 3.19, Pillow 12.3.0). Both
behave identically on the checks below. Taking Stage 19 as the example — with
django-sortedm2m 4.0.0, psycopg2-binary 2.9.12 and gunicorn 26.0.0 — the stack:

* imports and starts (``django.setup()`` with all eleven apps, including
  ``grappelli.dashboard``, which this project's ``dashboard.py`` depends on);
* passes ``manage.py check`` with **no issues**;
* resolves a URLconf containing ``grappelli.urls``, ``admin.site.urls`` and the
  namespaced ``photologue.urls``;
* reports **no pending migrations** for any installed app.

``pipdeptree`` on that environment gives the whole runtime tree::

    django-grappelli==5.0.0
    django-photologue==3.20
    ├── Django [required: >=5.2,<6.1, installed: 6.0.7]
    │   ├── asgiref [required: >=3.9.1, installed: 3.12.1]
    │   └── sqlparse [required: >=0.5.0, installed: 0.5.5]
    ├── django-sortedm2m [required: >=4.0.0, installed: 4.0.0]
    └── pillow [required: >=12.0.0, installed: 12.3.0]
    gunicorn==26.0.0
    └── packaging [required: Any, installed: 26.2]
    psycopg2-binary==2.9.12

Note photologue's ``Django>=5.2,<6.1``: **photologue is the ceiling on the whole
project's future**, not just its past. When Django 6.1 ships there will be no
compatible photologue until upstream releases one. Grappelli behaves the same
way. Both are worth watching — or, in the longer run, worth designing out.


Part 1 — What is installed today
================================

Runtime (``requirements/production.txt``, Python 2.7)
-----------------------------------------------------

============================ ========= =========================================
Package                      Pinned    Notes
============================ ========= =========================================
``django``                   1.6.11    The last 1.6 patch release; 1.5.1 until
                                       Stage 1, 1.5.12 until Stage 3
``django-photologue``        3.0.2     Owns database schema. The hard pacer.
                                       2.6.1 until Stage 2, 2.8.3 until Stage 4
``django-grappelli``         2.5.7     Admin skin. The other hard pacer. One
                                       series per Django release, so 2.4.5
                                       until Stage 3 moved the framework
``django-extensions``        1.6.7     Was in ``INSTALLED_APPS``; nothing
                                       imports it. **Development only** since
                                       Stage 0 -- ``dev.txt`` and
                                       ``local_settings.development.py``.
                                       1.5.9 until Stage 3
``django-jqm``               1.1.0.2   ``akaihola`` fork; was installed from
                                       GitHub, now vendored (issue 031)
``gunicorn``                 0.17.4    Production and, since issue 044,
                                       development server
``psycopg2-binary``          2.8.4     ``2.8.6`` is the last 2.8 patch
``six``                      1.11.0    Nothing in this repo imports it -- it was
                                       django-extensions', and left production
                                       with it at Stage 0
``south``                    1.0.2     Pre-1.7 migrations. Dies at Django 1.7.
                                       0.8.1 until Stage 3; 1.0.2 is the last
                                       release there is
============================ ========= =========================================

Plus ``Pillow==6.2.2`` — photologue's imaging backend, the last Pillow that
runs on Python 2.7. It was installed by ``dev/Containerfile`` and therefore
invisible to ``production.txt`` when this was written; issue 027 has since
moved it into the file, which now names the whole runtime set.

``django-sortedm2m==1.5.0`` was installed alongside it and left with issue 027:
the suspicion recorded here — that photologue 2.6.1 does not actually need it —
was confirmed by reading the installed metadata and grepping the package, and
the image builds and the suite passes without it. It came back with photologue
2.8, which is Stage 2 below -- at **0.7.0**, not at the version that used to be
here, and in ``requirements/production.txt`` rather than in an image
definition. Stage 4 raised it to **0.8.1**, which photologue 3.0.2 declares as
a floor.

``django-indexer==0.3.0`` and ``django-paging==0.2.4`` were in this list when it
was written, referenced by nothing; Stage 0 has since removed them (issue 020),
which is why the container no longer installs them.

None of the pinned production releases declare ``install_requires`` in the
metadata PyPI publishes, so the tree looks completely flat from outside — which
is why ``--no-deps`` plus hand-picked extras was needed. It is not flat once
they are built: issue 027 read the ``dist-info`` in the image and found
photologue 2.6.1 declaring ``Django>=1.4``, ``South>=0.7.5`` and
``Pillow>=2.0.0``, and django-extensions declaring ``six>=1.2``. Those four are
the whole implicit tree for this stage, all of them pinned, so ``--no-deps``
and a plain resolve produce the same set and the extras are gone. The tree is
now split across two files rather than one: Stage 0 moved django-extensions --
and therefore ``six``, its only consumer in the set -- into ``dev.txt``, so
``production.txt`` is seven packages whose only implicit edge is photologue's
``Pillow``, and ``dev.txt`` is that file plus three lines.

Test and development
--------------------

``requirements/testing.txt``
    ``pytest==3.5.0``, ``pytest-django==2.9.1``, ``coverage==4.5.4``,
    ``mock==2.0.0``, ``pbr==4.0.2``.
    pytest 3.5.0 pulls ``py``, ``six``, ``attrs``, ``more-itertools``,
    ``pluggy<0.7``, ``funcsigs``, ``setuptools``. These five held through
    Stage 6 and moved at Stage 7, the first stage that touches this file:
    ``pytest-django==3.1.2``, ``pytest==3.10.1``, ``coverage==5.5``, the other
    two unchanged. pytest 3.10.1 pulls ``atomicwrites`` and ``pathlib2`` as
    well, and lifts the ``pluggy<0.7`` ceiling.

``requirements/dev.txt``
    ``django-extensions==1.6.7`` (1.5.9 until Stage 3), ``flax``
    (``akaihola`` fork, GitHub),
    ``Fabric==1.6.0``, ``Werkzeug==0.8.3``. ``django-pserver`` was here too,
    and Stage 0 removed it (issue 033). ``flax`` and ``Fabric`` have gone the
    same way since, ahead of the Stage 10 this table put them in: they existed
    only for ``fabfile.py``, which issue 032 deleted. Three pins are left --
    ``django-extensions``, ``Werkzeug`` (what its ``runserver_plus`` imports,
    undeclared) and ``six`` (what its metadata declares) -- on top of an
    ``-r production.txt`` this file
    did not have when the table was written. Since Stage 0 it is what
    ``dev/Containerfile`` installs, so the development image is the runtime
    set plus those three.

``requirements/integration-tests.txt`` — **deleted since**
    ``pytest==4.6.9``, ``selenium==3.141.0``, ``pytest-selenium==1.17.0``,
    ``pytest-html==1.22.1``, ``pytest-metadata``, ``pytest-variables``,
    ``pytest-base-url``, ``podman-compose`` — plus eleven pins
    (``atomicwrites``, ``configparser``, ``contextlib2``, ``funcsigs``,
    ``importlib-metadata``, ``more-itertools``, ``pathlib2``, ``py``,
    ``scandir``, ``wcwidth``, ``zipp``) that existed **only** to keep pytest
    4.6.9 alive on Python 2.7. Issue 017 removed the file with the browser
    suite it belonged to, so all thirteen packages and all eleven backports are
    already gone rather than waiting for Python 3: the browser tests that
    replaced them run on the host's Python 3 and pin themselves, in
    ``browser_tests/requirements.txt``. The stages below are unaffected — this
    file was never installed into the application image.


Part 2 — The hard constraints
=============================

Five independent ladders have to be climbed at once. Whichever is shortest at
any moment is what blocks progress.

2.1 Django ↔ Python
-------------------

From each release's ``requires_python`` / classifiers:

========= ===================== ==========================================
Django    Python                Remark
========= ===================== ==========================================
1.5–1.6   2.6, 2.7, 3.2, 3.3
1.7       2.7, 3.2–3.4
1.8 LTS   2.7, 3.2–3.5
1.9–1.10  2.7, 3.4, 3.5
**1.11**  **2.7, 3.4–3.7**      **Last Django with Python 2. The bridge.**
2.0       3.4–3.7               Python 3 only from here on
2.1       3.5–3.7
2.2 LTS   3.5–3.9
3.0–3.1   3.6–3.9
3.2 LTS   3.6–3.10
4.0–4.1   3.8–3.11
4.2 LTS   3.8–3.12
5.0       3.10–3.12
5.1       3.10–3.13
5.2 LTS   3.10–3.14
6.0       3.12–3.14
========= ===================== ==========================================

**Consequence:** Python 2.7 → 3.x can only happen on Django 1.11. There is no
other version that runs on both. The Python flip is therefore locked to a
single point in the sequence, and everything before it is Python 2 work.

2.2 Django ↔ django-grappelli
-----------------------------

Grappelli ships exactly **one series per Django version**, stated in its own
README (quoted verbatim from each release):

=================== ==========================
Grappelli           Django
=================== ==========================
2.4.x (2.4.12)      1.4 / 1.5
2.5.x (2.5.7)       1.6
2.6.x (2.6.5)       1.7
2.7.x (2.7.3)       1.8
2.8.x (2.8.3)       1.9
2.9.x (2.9.1)       1.10
2.10.x (2.10.4)     1.11 (LTS)
2.11.x (2.11.2)     2.0
2.12.x (2.12.4)     2.1
2.13.x (2.13.4)     2.2 (LTS)
2.14.1–2.14.2       3.0
2.14.4              3.1
2.15.x (2.15.7)     3.2 (LTS)
3.0.x (3.0.10)      4.0 → 4.2 (LTS)
4.0.x (4.0.4)       5.x
5.0.0               6.x
=================== ==========================

**This is the pacer.** You cannot skip a Django version and keep a working
admin — and in this project the admin *is* the application. ``grappelli.dashboard``
(used by ``ylaneenkasvit/dashboard.py``) still exists in 5.0.0, verified by
listing the 5.0.0 sdist, so the dashboard survives the whole journey.

2.3 Django ↔ django-photologue
------------------------------

From photologue's own ``CHANGELOG.txt``:

=============== ==================== ==========================================
Photologue      Django               What changes for us
=============== ==================== ==========================================
2.6.1 (now)     1.4 – 1.5            South migrations. ``Photo.title_slug``.
2.7             1.4 – 1.5            All settings prefixed ``PHOTOLOGUE_``
2.8.3           1.4 – 1.5 (1.6 ?)    **Renames** ``title_slug`` → ``slug``;
                                     adds ``sites`` M2M; adds deps on
                                     ``django-sortedm2m`` + ``django-model-utils``
**3.0.2**       **1.6 – 1.7**        **Ships BOTH** ``south_migrations/`` **and**
                                     ``migrations/`` — the designated bridge
**3.1.1**       **1.6 – 1.7**        Also ships both. Last release that does.
3.2             1.7 – 1.9            Drops Django 1.6; **removes tagging**;
                                     drops ``django-model-utils``
3.4.1           1.8 – 1.9            Drops Django 1.7
3.6             1.8 – 1.10
3.7             1.8, 1.10, 1.11      Deprecates 1.9
3.8.1           1.11, 2.0            Drops 1.8 and 1.10
3.9             1.11 – 2.1           First checked on Python 3.7
3.10            1.11 – 2.2
3.11            2.0 – 3.0            **Drops Python 2**, Python 3.4, Django 2.1
3.13            – 3.1
3.14            – 3.2
3.15.1          – 4.0
3.16            3.2, 4.1, 4.2        Drops 2.2, 4.0 and Python 3.7
3.18            4.2 – 5.2            Drops 3.2 and 4.1
3.19 / 3.20     ``>=5.2,<6.1``       Python ``>=3.10``; **3.20 drops ExifRead**
=============== ==================== ==========================================

That 3.0.x and 3.1.1 are the only releases carrying both migration systems is
confirmed by listing their sdists — both have ``photologue/south_migrations/``
*and* ``photologue/migrations/``. 2.8.3 has South migrations under
``migrations/``; 3.2 onwards have Django migrations only. The 3.0 changelog says
it outright:

    *If you're upgrading to Django 1.7 — upgrade Photologue first, THEN upgrade
    Django.*

**The one unverified link in the chain.** Photologue's ``setup.py`` carries no
``Framework :: Django`` classifiers before 3.20, so its supported range comes
entirely from the changelog — and the changelog never states an *upper* bound
for 2.8.3. That 2.8.3 works on Django 1.5 is certain (3.0 is the release that
dropped 1.5). That it also works on Django 1.6 — which Stage 3 relies on for the
duration of one stage — is likely but untested. If it does not hold, collapse
Stages 3 and 4 into a single commit that moves Django 1.5.12 → 1.6.11 and
photologue 2.8.3 → 3.0.2 at once.

2.4 Django ↔ pytest-django (the safety net)
-------------------------------------------

From each release's ``tox.ini`` envlist:

================== =================== =====================
pytest-django      Django              pytest
================== =================== =====================
2.9.1 (now)        1.4 – **1.9**       >=2.5, <3.6 in practice
3.0.0 / 3.1.2      1.7 – 1.10          >=2.9 / 3.0
3.2.1              1.8 – 2.0           >=2.9
3.4.8              1.8 – 2.2           >=3.6
3.10.0             1.8 – 3.1           >=3.6 (last with Python 2.7)
4.5.2              2.2 – 4.0           >=5.4
4.6.0 – 4.8.0      3.2 – 5.0           >=7.0
4.11.1             4.2 – 5.2           >=7.0
4.12.0             4.2 – 6.0           >=7.0, Python >=3.10
================== =================== =====================

``requirements/testing.txt`` used to carry the comment "pytest-django 2.9.1 is
the last release supporting Django 1.5", which is correct; it is *also* the case
that 2.9.1 keeps working all the way to **Django 1.9**, so the test stack held
through six stages of framework moves. Stage 7 is where it moved, to 3.1.2, one
stage ahead of the Django 1.10 that would have forced it.

Two things Stage 7 measured about that move, both of them about the pair rather
than about either release. 3.0.0 moved the guard against unmarked database
access from the cursor level to the connection level, so a test that touches the
database without ``@pytest.mark.django_db`` fails at 3.1.2 where 2.9.1 let it
through; no test in this suite did. And 3.1.2 reads marks through pytest's
``MarkInfo``, which pytest 3.6 deprecated, so pairing it with pytest 3.10.1
costs 456 warnings from one line of the plugin. The Stage 7 record has what that
cost and what bought it back.

2.5 psycopg2
------------

Django's own hard minimum, read out of ``django/db/backends/postgresql/base.py``:

* Django ≤ 3.2: ``psycopg2 >= 2.5.4``
* Django 4.0 – 5.2: ``psycopg2 >= 2.8.4``; psycopg **3** supported from 4.2
* Django 6.0: ``psycopg2 >= 2.9.9``

There is one non-obvious ceiling. Django ≤ 3.0 ships::

    # django/db/backends/postgresql/utils.py
    def utc_tzinfo_factory(offset):
        if offset != 0:
            raise AssertionError("database connection isn't set to UTC")
        return utc

Issue :doc:`issues/084-django-3-1-is-the-next-runtime-upgrade`, "Timezone compatibility",
records the callback change and its PostgreSQL check. The version boundary is:

    **psycopg2-binary must stay < 2.9 until Django ≥ 3.1.**

``psycopg2-binary`` availability: 2.7.7 (py2.6+), 2.8.6 (py2.7 – 3.8),
2.9.x (py3.6+, latest 2.9.12 requires 3.9+).

2.6 Everything else
-------------------

============================ =========================================================
Package                      Ladder
============================ =========================================================
``django-sortedm2m``         **0.7.0** at Stage 2 — photologue 2.8.3 declares
                             ``<0.8`` and the production image's ``manage``
                             enforces it — then **0.8.1 or above at Stage 4**,
                             which photologue 3.0.2 declares as a *floor* where
                             2.8.3 declared a ceiling, so the pin must move in
                             that stage's own change (measured at Stage 3);
                             then 1.1.1 at Stage 6 (photologue 3.4.1's floor,
                             and the release upstream wrote that floor for
                             because of Django 1.9 — **so it stays at Stage 7**,
                             which this row used to schedule 1.3.3 in);
                             then 1.3.3 at Stage 9 (photologue 3.7's
                             floor) → 1.5.0 (Dj ≤1.9) → 2.0.0 (1.11–2.2)
                             → 3.0.0 (2.2–3.0) → 3.1.1 (2.2–3.2) → 4.0.0 (4.2–5.1)
``Pillow``                   6.2.2 last on py2.7 · 7.0 needs 3.5 · 9.0 → 3.7 ·
                             10.0 → 3.8 · 12.0 → 3.10. **Also capped from above
                             by photologue** — ``<10`` up to photologue 3.15.1,
                             ``>=9.1`` from 3.16. See 3b.1; 9.5.0 satisfies both.
``ExifRead``                 2.1.2+ needed by photologue 3.4–3.19; 3.x needs py≥3.7;
                             not needed at all from photologue 3.20. API stable
                             throughout — see 3b.4.
``django-model-utils``       needed only by photologue 2.8 – 3.1, and **≤ 2.3.1**:
                             2.4 deleted ``PassThroughManager``, which is the one
                             thing photologue imports from it. Measured at Stage 2;
                             nothing declares this bound.
``gunicorn``                 0.17.4 → 19.6.0 still ship the ``run_gunicorn`` Django
                             command; **19.7.1 removed it**. 20.0 needs py3.4,
                             24.0 needs py3.10. **≤20.1.0 imports ``pkg_resources``
                             and so needs ``setuptools<82``; 21.2.0 does not.**
                             Go straight to 21.2.0 — see 3b.2.
``django-extensions``        1.5.9 (Dj 1.4–1.8) → 1.6.7 (1.6–1.9) → 1.7.9 (1.8–1.11)
                             → 1.9.9 (1.8–2.0) → 2.2.9 (1.11–3.0, last with py2.7)
                             → 3.1.5 (2.2–3.2) → 3.2.3 (3.2–4.2) → 4.1 (4.2–5.2)
``coverage``                 **5.5** is the last release supporting Python 2.7
                             (``>=2.7,<4``); 6.0 requires 3.6+. The 4.5.4 pin is
                             conservative — 5.5 can be adopted at any time.
``mock`` / ``pbr``           superseded by ``unittest.mock`` on Python 3
``Fabric``                   1.x is py2-only up to 1.14.1; 1.15.0 added py3;
                             2.x/3.x are a rewrite with a different API.
                             **Gone** -- issue 032, deleted rather than ported
``Werkzeug``                 1.0.1 is the last with py2.7; 2.x needs 3.6+
``selenium``                 3.141.0 is the last with py2.7; 4.x is a new API
============================ =========================================================


Part 3 — Django API removals, and what they hit here
====================================================

.. _`Django API removals`:

Observed by grepping the actual Django source of every release. "Gone in" means
the module/name is no longer present in the shipped package.

==================================================== ======== =====================================================
Django API                                           Gone in  Used by
==================================================== ======== =====================================================
``django.conf.urls.defaults``                        **1.6**  — *done at Stage 3*: both ``urls.py`` import ``django.conf.urls``
``DATABASES[...]['TEST_NAME']``                      1.8      — *done at Stage 5*: ``test_settings.py`` uses ``'TEST': {'NAME': …}``
``django.contrib.admin.util``                        1.9      — (the fork that used it went at Stage 5)
``EMPTY_CHANGELIST_VALUE``                           1.9      — (same)
``django.db.models.get_model``                       1.9      —
``SubfieldBase``                                     1.10     —
``django.core.context_processors``                   1.10     — *done at Stage 6*: the ``TEMPLATES`` entry names ``django.template.context_processors``
``TEMPLATE_DIRS`` / ``TEMPLATE_CONTEXT_PROCESSORS``  1.10     — *done at Stage 6*: one ``TEMPLATES`` setting
string view names in ``url()``                       1.10     — *done at Stage 8*: four imported callables; the fourth was in ``kasvimuseo/urls.py``
``patterns()``                                       **1.10** — *done at Stage 8*: plain lists (this row said 2.0 until Stage 7 observed 1.10.8 without it)
``django.core.urlresolvers``                         2.0      — *done at Stage 8*: ``django.urls`` on all 15 import lines
``force_unicode``                                    2.0      — (same)
``MIDDLEWARE_CLASSES`` (and its default)             2.0      — *done at Stage 8*: renamed to ``MIDDLEWARE``; see below
``ForeignKey`` without ``on_delete``                 2.0      ``kasvimuseo/models.py`` (13 sites)
``django.contrib.auth.views.login`` / ``logout``     2.1      ``ylaneenkasvit/urls.py``
``django.utils.six``                                 3.0      —
``render_to_response``                               3.0      — *done at Stage 8*: ``planted_observation`` calls ``render()``
``postgresql_psycopg2`` ENGINE alias                 3.0      ``common_settings.py``
``ugettext`` / ``ugettext_lazy``                     **4.0**  ``models.py``, ``admin.py``, ``dashboard.py``
``force_text`` / ``smart_text``                      4.0      ``ylaneenkasvit/dashboard.py``
``DEFAULT_FILE_STORAGE`` / ``STATICFILES_STORAGE``   5.1      — (set ``STORAGES`` from 4.2)
``index_together``                                   5.1      —
==================================================== ======== =====================================================

Three more removals hit ``kasvimuseo_admin_list.py`` and are not in that table,
because they were found later, while deciding issue 034: ``_meta.module_name``
(gone in **1.8**), ``_meta.get_field_by_name`` (gone in **1.10**) and
``django.db.models.FieldDoesNotExist`` (deprecated at 1.8 in favour of
``django.core.exceptions.FieldDoesNotExist``). All three are inside
``identifier_for_field``, the one function in that file Django has no equivalent
of. Deleting the file in Stage 5 pre-empts all three, along with the four rows
above that now read "—".

Two settings landmines that a grep does not show, because the settings are
*missing*:

**No MIDDLEWARE at all.** ``common_settings.py`` never defines
``MIDDLEWARE_CLASSES`` or ``MIDDLEWARE``; the site runs on the
``global_settings`` default. Django 1.10 introduced ``MIDDLEWARE`` with a default
of ``None`` and Django **2.0 deleted** ``MIDDLEWARE_CLASSES`` and made
``MIDDLEWARE`` default to ``[]``. At Django 2.0 the site will therefore run with
*no middleware whatsoever* — no sessions, no auth, no CSRF, no admin — and it
will not raise an obvious error. Define ``MIDDLEWARE`` explicitly **now**, while
it is still just a no-op restatement of the current default. *Done* -- issue 019
wrote the 1.5 default out into ``common_settings``, under the name Django 1.5
reads; Stage 8 renamed it.

**No** ``django.contrib.messages`` **app.** Its context processor is configured
but the app is not in ``INSTALLED_APPS``. The admin requires it from Django 1.7
onwards. Add it in Stage 0. *Done* -- issue 023 added the entry; the app carries
no models, so nothing had to be migrated for it.

Python 2 → 3 code work (Stage 10)
---------------------------------

* ``__unicode__`` on 12 model/class definitions → ``__str__``
* ``unicode(...)`` at 3 sites
* ``force_unicode`` / ``smart_str`` → ``force_text`` / ``smart_text``
* ``kasvimuseo/forms.py``: ``remove_diacritics`` **was**
  ``filter(lambda x: not combining(x), normalize('NFKD', u))``. On Python 2 that
  returns a string; on Python 3 it returns an iterator, and ``slugify()`` would
  have received ``<filter object …>`` -- a **silent** data corruption bug, not a
  crash. Done ahead of the stage (issue 016): it is a ``u''.join(...)`` over the
  same condition, which returns a text string on both versions and returned
  exactly what ``filter()`` did on Python 2.
* ``common_settings.py`` used to hardcode
  ``here('..', 'lib', 'python2.7', 'site-packages', 'photologue', 'templates')``
  in ``TEMPLATE_DIRS``. **Done already** (issue 024): the entry is deleted and
  photologue's templates come from the app template loader, which is in the
  Django 1.5 default ``TEMPLATE_LOADERS`` this project does not override. It
  had stopped resolving long before — nothing to do at this stage.
* ``u'…'`` literals (≈200) are valid again from Python 3.3; leave them alone.


Part 3b — Cross-package breakages
=================================

.. _`Part 3b — Cross-package breakages`:

These are the answer to "which package versions will be broken if other packages
are upgraded too far". None of them are visible in dependency metadata; all three
were found by actually resolving each stage with ``uv`` and then reading the
source of what it selected.

The root cause is the same in every case: **the old packages declare only
lower bounds.** photologue says ``Pillow>=6.0.0`` and means "6.0 or the handful
of releases after it"; a resolver reads it as "anything from 6.0 to the heat
death of the universe" and picks Pillow 12.

3b.1 photologue ≤ 3.15.1 versus Pillow ≥ 10
-------------------------------------------

Observed directly in ``photologue/models.py`` across every release, and in
``PIL/Image.py`` across every Pillow wheel:

=========================== =========================================
photologue                  Resampling API used
=========================== =========================================
2.6.1 … **3.15.1**          ``Image.ANTIALIAS``
**3.16** … 3.20             ``Image.Resampling.LANCZOS``
=========================== =========================================

=========================== =========================================
Pillow                      State
=========================== =========================================
… 9.0.0                     ``ANTIALIAS`` present, no ``Resampling``
9.1.0 … 9.5.0               both present (the overlap window)
**10.0.0** …                ``ANTIALIAS`` **removed**
=========================== =========================================

Confirmed at runtime on Pillow 12.3.0::

    >>> PIL.Image.ANTIALIAS
    AttributeError: module 'PIL.Image' has no attribute 'ANTIALIAS'

photologue ≤ 3.15.1 also uses ``Image.FLIP_LEFT_RIGHT`` and
``Image.ROTATE_180``, but **those are fine** — they still exist in Pillow 12 as
module-level aliases. ``ANTIALIAS`` is the only casualty.

So:

* **photologue ≤ 3.15.1 requires ``Pillow<10``.** Every stage from 2 through 16
  needs that upper bound written down.

  Note *where* it fails. The call sits in ``ImageModel.resize_image()``, reached
  from ``create_size()``, which is called from ``_get_SIZE_url()`` — the lazy
  accessor behind ``photo.get_display_url()``, and only *when the cached file
  does not already exist*::

      def _get_SIZE_url(self, size):
          photosize = PhotoSizeCache().sizes.get(size)
          if not self.size_exists(photosize):
              self.create_size(photosize)     # <-- AttributeError here

  ``kasvimuseo/photos.py`` calls ``get_display_url()`` for every photo on the
  species pages, so this surfaces as a **500 on page render**, not at upload and
  not at startup. And because it is guarded by ``size_exists()``, a developer
  with a warm cache directory will never see it while production, or anyone who
  ran ``media fetch`` without the derived sizes, breaks immediately. Nothing
  short of rendering a page with an uncached photo size will catch it.
* **photologue ≥ 3.16 requires ``Pillow>=9.1``, not ``>=9``.** Its own metadata
  says ``Pillow>=9``, which is wrong by one minor version: ``Image.Resampling``
  does not exist in Pillow 9.0.0. Constrain it yourself.

Pillow 9.5.0 is the last release that satisfies both sides, and it is the right
pin for every stage up to and including 16.

**Decided** (issue 028). ``Pillow<10`` through Stage 16 and ``Pillow>=9.1``
from Stage 17, with 9.5.0 as the pin for everything in between; Stage 10 is
where 6.2.2 becomes 9.5.0. The constraint is written where the versions are
set rather than only here: beside the ``Pillow==6.2.2`` pin, beside
``django-photologue`` -- the pin that implies it -- and beside the resolution
in the production ``Dockerfile``. Nothing was upgraded to record it. The first
two of those were in ``dev/Containerfile`` and ``requirements/production.txt``
respectively when 028 was settled, because the file did not name Pillow at all;
issue 027 has since moved the pin into ``production.txt``, so both now sit
there, a few lines apart.

Measured while recording it: with ``Image.ANTIALIAS`` deleted, the suite fails
five tests, not none. Four are the admin photo changelist, which builds
``admin_thumbnail`` -- a *cropping* size, and photologue's crop branch resizes
unconditionally. The public reports use ``display``, which does not crop, and
the non-crop branch returns early rather than upscale, so no test had ever
scaled an image down. The fifth is the one added with this decision,
``test_reports_build_an_uncached_photo_size``: a species report, a cold cache
and a photo twice the ``display`` size. Both call sites are now covered, and
the page the garden actually serves is one of them.

3b.2 gunicorn ≤ 20.1.0 versus setuptools ≥ 82
----------------------------------------------

``pkg_resources`` — the import — appears in:

=================== ==============================================
gunicorn            ``pkg_resources`` imported in
=================== ==============================================
19.10.0             ``util.py``, ``app/pasterapp.py``
20.1.0              ``util.py``, ``workers/ggevent.py``,
                    ``workers/geventlet.py``
**21.2.0** …        nothing
=================== ==============================================

and ``setuptools`` **82.0.0 stopped shipping ``pkg_resources`` altogether**
(present through 81.0.0, gone from 82.0.0).

Unbounded resolution of Stages 13–15 selects ``gunicorn==20.1.0`` *and*
``setuptools==82.0.1`` together, which is a gunicorn that cannot start.

The fix is free: **go to gunicorn 21.2.0 as early as Stage 10.** It requires only
Python ≥ 3.5, it is independent of Django, and it removes the constraint
permanently. There is no reason to spend stages sitting on gunicorn 20.

**Decided** (issue 029). That is the ruling: 0.17.4 → 21.2.0 at Stage 10,
skipping 19.x and 20.x, and **no** ``setuptools<82`` bound is carried by any
stage. Stage 10 says so, and the reason is recorded beside the ``gunicorn``
pin in ``requirements/production.txt``, which is the only place the version is
set. The pin itself does not change here: 0.17.4 runs on Python 2.7, where
setuptools 82 does not exist. Nothing else depends on the choice --
``dev/kasvimuseo app run`` has served the development site through gunicorn
since issue 044, but it runs the same interpreter and the same pin as
production, so it is affected exactly when production is, which today is not
at all. The one thing to carry into Stage 10 is that 19.7.1 removed the
``run_gunicorn`` management command, which is skipped over rather than passed
through: nothing in the repository invokes it -- ``dev/kasvimuseo app run``
runs the ``gunicorn`` executable -- and the ``INSTALLED_APPS`` entry that
command needed is issue 021.

3b.3 django-sortedm2m < 2.0.0 cannot be built by a modern toolchain
--------------------------------------------------------------------

sortedm2m 1.1.1 through 1.5.0 are **sdist-only** — no wheels were ever
published, so every install builds from source. Their ``setup.py`` wraps
``long_description`` in a custom ``UltraMagicString`` class, and modern
setuptools does::

    File "setuptools/_core_metadata.py", line 221, in write_pkg_file
        if not long_description.endswith("\n"):
    AttributeError: 'UltraMagicString' object has no attribute 'endswith'

Wheels first appear at 2.0.0. This bites Stages 2 and 4–11, which need
sortedm2m 1.1.1 → 1.5.0 to match their photologue.

Not a blocker, but it dictates *how* those stages are built: they must run
inside a period-appropriate image with an old ``setuptools`` (< 60) and an
interpreter that still has ``distutils`` (< 3.12). That is already true of the
Python 2.7 container, and stays true for a Python 3.7 one. It only becomes a
problem if someone tries to rebuild an early stage on a current machine.

*This one could not be fully verified here:* the workaround needs
``setuptools<60``, which will not import on Python 3.12+ (no ``distutils``), and
no older interpreter was available. The failure is confirmed; the fix is
inferred.

**Decided** (issue 030). Nothing to pin and nothing to change: the constraint
is on the *builder*, not on the version, and every stage that needs sortedm2m
1.1.1-1.5.0 is built in an image old enough to satisfy it. What was owed was
the record, and it is beside the place the package is named, so that a build
failure on a current machine is recognised rather than debugged from scratch.
That place has moved: the record sat beside a ``django-sortedm2m==1.5.0`` pin
in ``dev/Containerfile`` until issue 027 established that photologue 2.6.1 does
not use the package and removed it from the image, so it is now the comment in
``requirements/production.txt`` that says why the package is absent and when --
Stage 2 -- it arrives. Nothing about this ruling changed.
Should a stage ever have to be built on a modern toolchain, the way out is
sortedm2m 2.0.0, the first release with a wheel -- which is a Django 1.11
floor and therefore not available before Stage 9.

**The hedge above no longer applies.** An interpreter with ``distutils`` was
available after all (``nix-shell -p python311``), so the workaround was
measured: on Python 3.11.15, ``django-sortedm2m==1.5.0`` builds and installs
under setuptools 59.8.0 and fails under 83.0.0 with exactly the
``UltraMagicString`` traceback above. The boundary is the setuptools in the
environment, not the Python version -- and pip does not isolate the build of
these sdists, because they carry no ``pyproject.toml``, so the ambient
setuptools is the one that decides. The Stage 10 image was checked too:
``python:3.7-alpine`` ships setuptools 57.5.0 and installs sortedm2m 1.5.0
without complaint. Issue 030 has the numbers.

**And the version is 0.7.0 rather than a 1.x from Stage 2 onwards**, for
reasons that have nothing to do with the builder -- see Stage 2 -- so read
"1.1.1 through 1.5.0" above as this section's own title reads: everything
below 2.0.0. 0.7.0 is sdist-only as well, with the same ``UltraMagicString``
in the same ``setup.py``, so the constraint is unchanged and so is the way
out.

3b.4 What is *not* a problem
-----------------------------

Worth recording, so nobody re-investigates:

* **ExifRead is safe across the whole range.** photologue calls exactly one
  function, ``exifread.process_file``, and it is present and unchanged from
  2.1.2 through 3.5.1. The 2.x → 3.x major bump does not affect this project.
* **pytz is safe.** Django 1.11–3.2 depend on it unbounded, but pytz is a data
  package with a stable API; a 2026 release works with Django 1.11.
* **sqlparse and asgiref are safe** — Django bounds them itself
  (``asgiref<4``, ``sqlparse>=0.3.1``).

The general rule this implies
------------------------------

**Every stage's requirements file must be a full lock, not a list of direct
pins.** This used to be done in ``dev/Containerfile``, by ``pip install
--no-deps`` plus two manually chosen extras, under a comment explaining that it
"avoids photologue dragging in an incompatible Pillow" — this analysis is that
comment, generalised and made explicit.

**Decided** (issue 027), and Stage 0 is now a full lock. It is
``requirements/production.txt``, maintained by hand: it names every runtime
package at an exact version, and the extras are gone. By hand because ``uv pip
compile --python-version 2.7`` answers *"Invalid version request: Python <3.6
is not supported but 2.7 was requested"* — run rather than assumed. Forced to
3.7 it reproduces the same set except for Pillow, where it picks 9.5.0: right
for Stage 10, uninstallable on Python 2.7.

So the mechanism to adopt — a short ``*.in`` per stage with the direct pins and
the upper bounds established above, plus a committed, generated fully-pinned
``*.txt`` — starts at **Stage 10**, the Python 3 flip, which is exactly where
`Appendix A — Resolved lock set per stage`_ begins. Stages 0–9 are locks in
the plain sense: complete, exact and written out by a person. Nothing before
Stage 10 gains a ``*.in`` file, because nothing before Stage 10 has a resolver
that could regenerate the ``*.txt`` from it.


Part 4 — The upgrade sequence
=============================

This sequence guides source upgrades. The private deployment repository owns installation measurements and migration rehearsal records.

Stage 0 — Dead weight and defensive settings (no version changes)
-----------------------------------------------------------------

:Status: Done
:Resolution: 2d01cde, and the issues this stage is made of: 019, 020, 021, 022,
    023, 024, 027 and 033

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 1 — Django 1.5.1 → 1.5.12
-------------------------------

:Status: Done
:Resolution: 48fda0e

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 2 — Photologue 2.6.1 → 2.8.3, still on Django 1.5
-------------------------------------------------------

:Status: Done
:Resolution: f539523

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 3 — Django 1.5.12 → 1.6.11
--------------------------------

:Status: Done
:Resolution: 9add8ba

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 4 — Photologue 2.8.3 → 3.0.2, still on Django 1.6
-------------------------------------------------------

:Status: Done
:Resolution: fa8ac5f

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 5 — Django 1.6.11 → 1.7.11: the South cut
-----------------------------------------------

:Status: Done
:Resolution: 67e0a28

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 6 — Django 1.7.11 → 1.8.19 (LTS)
--------------------------------------

:Status: Done
:Resolution: 52d7497

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 7 — Django 1.8.19 → 1.9.13
--------------------------------

:Status: Done
:Resolution: 9a92f79, 5c690c2, 1f16227, 693ae18, 83fd23e

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 8 — Django 1.9.13 → 1.10.8
--------------------------------

:Status: Done
:Resolution: 1851d45, 57edfff, d8cd291, 6a52576

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 9 — Django 1.10.8 → 1.11.29 (LTS)
---------------------------------------

:Status: Done
:Resolution: eb33c9a, 7f75d60

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 10 — **Python 2.7 → 3.7**, staying on Django 1.11.29
----------------------------------------------------------

:Status: Done
:Resolution: 51fe8ba, c32c664, ce3bc43

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 11 — Django 1.11 → 2.0.13
-------------------------------

:Status: Done
:Resolution: d1b5f89, c07bab2, 3d4e3f1

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 12 — Django 2.0 → 2.1.15
------------------------------

:Status: Done
:Resolution: 1b9b93e

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 13 — Django 2.1 → 2.2.28 (LTS)
------------------------------------

:Status: Done
:Resolution: 41e207e, 8a97f5f, dc78466

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 14 — Django 2.2 → 3.0.14
------------------------------

:Status: Done
:Resolution: Issue 083

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 15 — Django 3.0 → 3.1.14
------------------------------

:Status: Done
:Resolution: Issue 084

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 16 — Django 3.1 → 3.2.25 (LTS)
------------------------------------

:Status: Done
:Resolution: Issue 085

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 17 — Django 3.2 → 4.0.10 → 4.1.13 → 4.2.30 (LTS)
------------------------------------------------------

:Status: Done
:Resolution: Issue 086

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 18 — Django 4.2 → 5.0.14 → 5.1.15 → 5.2.16 (LTS)
------------------------------------------------------

:Status: Next

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Stage 19 — Django 5.2 → 6.0.7 (current)
---------------------------------------

:Status: Planned

Run the application, browser, migration, and documentation checks after this stage.
Use the dependency constraints above and the resolved locks in Appendix A.

Part 5 — Packages that stop being needed
========================================

=================================== ========= ==================================================
Package                             Dies at   Because
=================================== ========= ==================================================
``django-indexer``                  Stage 0   Never referenced. **Gone** -- issue 020
``django-paging``                   Stage 0   Never referenced. **Gone** -- issue 020
``django-pserver``                  Stage 0   Only ever in a commented-out line.
                                              **Gone** -- issue 033
``gunicorn`` as an *app*            Stage 0   ``run_gunicorn`` removed in gunicorn 19.7.1.
                                              **Gone** -- issue 021; the package stays
``django-jqm`` as a *dependency*    Stage 0   Vendored into the repo.
                                              **Gone** -- issue 031
``south``                           Stage 5   Django 1.7 ships migrations
``django-model-utils``              Stage 6   Photologue 3.2: "Django can now natively chain
                                              custom manager filters"
``django-tagging`` shim             Stage 6   Photologue 3.2 removed tagging
``six``                             Stage 10  Python 3 only. **Out of production
                                              already** -- Stage 0. "Python 3
                                              only" was the wrong reason: it was
                                              in the image because
                                              django-extensions declares it, and
                                              it followed that package into
                                              ``dev.txt``. What Stage 10 deletes
                                              is a development pin
``mock`` + ``pbr``                  Stage 10  ``unittest.mock`` since Python 3.3
Python 2 backports [1]_             Stage 10  Pinned only to keep pytest 4.6.9 on Python 2.7
``Fabric`` + ``flax``               Stage 10  Fabric 1.x is Python 2 only, and
                                              Private deployment tooling owns this work —
                                              delete rather than port to Fabric 3.
                                              **Gone** -- issue 032, and ahead of
                                              this stage: nothing about it needed
                                              Python 3 to be decided
``pytz``                            Stage 17  Django 4.0 switched to ``zoneinfo``
``ExifRead``                        Stage 19  Photologue 3.20 dropped it
``Werkzeug``                        optional  Only for django-extensions' ``runserver_plus``
``psycopg2-binary``                 optional  ``psycopg[binary]`` is supported from Django 4.2
=================================== ========= ==================================================

.. [1] ``atomicwrites``, ``configparser``, ``contextlib2``, ``funcsigs``,
   ``importlib-metadata``, ``more-itertools``, ``pathlib2``, ``py``,
   ``scandir``, ``wcwidth``, ``zipp``.


Part 6 — Other things to take into account
==========================================

The admin-list fork is deleted in Stage 5
-----------------------------------------

``kasvimuseo/templatetags/kasvimuseo_admin_list.py`` (235 lines) is a
copy-and-modify fork of Django's own
``django/contrib/admin/templatetags/admin_list.py``. It imports six private
admin symbols and reimplements ``result_headers``, ``items_for_result`` and
``results``. This section used to say the file must be re-synced at every single
Django stage — nineteen times — and that this was plausibly more work than all
the other code changes combined. **Issue 034 ruled otherwise, and the file goes
in Stage 5.** The four steps are listed there; this is why.

Its only purpose is to put the field name into each ``<td class="...">``, and
Django does that itself from **1.7**, which is the version Stage 5 installs.
Ticket #11195 — the ticket this fork's own docstring cites — was closed in 1.7:
"The admin changelist cells now have a ``field-<field_name>`` class in the HTML
to enable style customizations". Stock ``items_for_result`` emits
``field-<name>`` on cells and ``result_headers`` emits ``column-<name>`` on
headers; from 1.10 ``_coerce_field_name`` also names callables in
``list_display`` exactly as the fork's ``identifier_for_field`` does. So the
fork stops being a customisation at Stage 5 and becomes a duplicate.

Measured while deciding this, rather than estimated:

* A mechanical diff of the three forked functions against the installed Django
  1.5.1 copy is six hunks, ``-9 / +22`` lines; ``results`` is byte-identical.
  Every difference is a CSS class. The rest of the file is Django's. Still
  true after Stage 1: ``contrib/admin/templatetags/admin_list.py`` is one of
  the files that does *not* differ between the 1.5.1 and 1.5.12 sdists, so the
  fork is no more and no less stale than it was.
* Three selectors in the whole repository consume those classes, all in
  ``kasvimuseo/static/css/kasvimuseo.admin.css``, and only one of them —
  ``.fieldname_edit``, in ``@media print`` — is fully live. The
  ``#changelist-form td.fieldname_admin_thumbnail`` rule has never matched
  anything, because this project's ``change_list.html`` renders grappelli's
  ``#grp-changelist-form``; and ``.fieldname_action_checkbox`` reaches the body
  cells but not the header, so printing a changelist today leaves the header row
  one cell wider than the body. Both are repaired by the Stage 5 CSS step.
* Carrying the fork would cost 343 changed lines across 15 of the 19 stage
  transitions (largest: 3.2 → 4.0 at 96 lines, 1.6 → 1.7 at 80), plus seven
  import repairs — the four in `Django API removals`_ and the three named under
  that table.

The option of re-deriving the fork once from Django 6.0's source at the end was
considered and rejected as circular: 6.0's source already emits these classes,
so the re-fork would be Django's own file with one string changed, and the
import repairs would still have to be paid on the way there.

**Until Stage 5 the file is frozen.** No stage before 5 edits it; nothing after
5 refers to it. A changelist markup change needed before then belongs in the CSS
or in ``kasvimuseo/admin.py``.

Schema migration checks
-----------------------

Developers must check upgrades against representative databases, including old schemas and inconsistent records.
Use fixtures without private data for public tests.
The private deployment repository owns checks against installation data.

The test suite is the gate, and it moves too
--------------------------------------------

The current pytest/pytest-django pins hold from Django 1.5 all the way to 1.9 —
five Django versions of free coverage. After that the test stack has to be
bumped in lockstep with Django (Part 2.4). Budget for the pytest 3 → 4 → 5 → 7
fixture and collection-API churn; it is not free.

The container base image
------------------------

``python:2.7-alpine`` has received no security updates since 2020, and neither
have the C libraries it links against. Each stage should also bump the base
image; the Python flip in Stage 10 is the point where this stops being a
liability.

Configuration checks
--------------------

The settings require environment variables for secrets and allowed host names.
``README.rst``, "Site configuration", lists those variables.

Suggested checkpointing
-----------------------

Stop and hold at the LTS releases: **1.11** (Stage 9, before the Python flip),
**2.2** (Stage 13), **3.2** (Stage 16), **4.2** (Stage 17) and **5.2**
(Stage 18). Each is a place where every dependency has a mature, well-tested
matching release, and where the project can sit indefinitely if the work has to
pause.

An honest estimate of where the effort is concentrated:

#. Stage 5 (South → Django migrations, on real data)
#. Stage 10 (Python 2 → 3)
#. Stage 2 (photologue ``title_slug`` → ``slug`` + sites framework)
#. Everything else, which is largely mechanical import rewrites

The recurring ``kasvimuseo_admin_list.py`` re-sync used to rank fourth on that
list. It is not on it any more: issue 034 retired the file rather than carrying
it, so what was nineteen re-syncs is now one deletion, in Stage 5.


Appendix A — Resolved lock set per stage
========================================

.. _`Appendix A — Resolved lock set per stage`:

Each set below is the **complete transitive closure** produced by
``uv pip compile --python-version <py>`` from that stage's direct pins, with the
upper bounds from `Part 3b — Cross-package breakages`_ applied. Runtime
(``production.txt``) only — test and development pins follow the ladders in
Parts 2.4 and 2.6.

Stages 0–9 run on Python 2.7, which ``uv`` cannot target, so they have no
generated lock. Build those the way the project already does: ``pip install
--no-deps`` against a hand-maintained pin list — which since issue 027 is a
complete one. Stage 0's is ``requirements/production.txt`` as it stands today:
ten packages, every one exact, ``Pillow==6.2.2`` among them, and no second
install anywhere adding to it. Each stage from 1 to 9 edits that file and stays
whole; ``--no-deps`` is what makes an omission show up as an ``ImportError``
in the image rather than as an unpinned package nobody chose.

The test stack
--------------

``testing.txt`` moves on its own schedule, driven by pytest-django (Part 2.4).
The direct pins per stage:

========== ============ ================= ========== ==========
Stage      Django       pytest-django     pytest     coverage
========== ============ ================= ========== ==========
0 – 6      1.5 – 1.8    2.9.1             3.5.0      4.5.4
7 – 8      1.9 – 1.10   3.1.2             3.10.1     5.5
9          1.11 (py2.7) 3.10.0            4.6.11     5.5
10 – 12    1.11 – 2.1   3.10.0            4.6.11     5.5
13 – 15    2.2 – 3.1    4.5.2             6.2.5      7.2.7
16         3.2          4.5.2             6.2.5      7.2.7
17         4.2          4.8.0             8.3.5      7.6.1
18         5.2          4.11.1            8.3.5      7.6.1
19         6.0          4.12.0            9.1.1      7.15.2
========== ============ ================= ========== ==========

Four of these were resolved to check they hold together. Stage 10, on
Python 3.7, is the awkward one — pytest 4.6.11 drags in the whole
``atomicwrites`` / ``more-itertools`` / ``py`` / ``zipp`` cluster::

    atomicwrites==1.4.1     more-itertools==9.1.0   pytest==4.6.11
    attrs==24.2.0           packaging==24.0         pytest-django==3.10.0
    coverage==5.5           pluggy==0.13.1          six==1.17.0
    django==1.11.29         py==1.11.0              typing-extensions==4.7.1
    importlib-metadata==6.7.0  pytz==2026.3.post1   wcwidth==0.2.14, zipp==3.15.0

By Stage 19 that has collapsed to nine packages total::

    asgiref==3.12.1   iniconfig==2.3.0   pluggy==1.6.0      pytest-django==4.12.0
    coverage==7.15.2  packaging==26.2    pygments==2.20.0   sqlparse==0.5.5
    django==6.0.7     pytest==9.1.1

``mock`` and ``pbr`` drop out at Stage 10 in favour of ``unittest.mock``.

Stage 10 — Django 1.11.29 (LTS), Python 3.7
-------------------------------------------

.. literalinclude:: ../requirements/production.txt
   :language: text

Issue :doc:`issues/077-python-3-runtime-needs-a-rehearsed-transition`, "Support checks", records the resolver and build toolchain.

Stage 11 — Django 2.0.13, Python 3.7
------------------------------------

::

    django-grappelli==2.11.2
    django-photologue==3.8.1
    django-sortedm2m==1.5.0
    django==2.0.13
    exifread==3.5.1
    gunicorn==21.2.0
    importlib-metadata==6.7.0
    packaging==24.0
    pillow==9.5.0
    psycopg2-binary==2.8.6
    pytz==2021.3
    typing-extensions==4.7.1
    zipp==3.15.0

``django-sortedm2m==1.5.0`` is pinned by hand — it is sdist-only and modern setuptools cannot
build it, so a resolver cannot select it (see 3b.3), but photologue's floor for
this stage requires it.

Stage 12 — Django 2.1.15, Python 3.7
------------------------------------

::

    django==2.1.15
    django-grappelli==2.12.4
    django-photologue==3.9
    django-sortedm2m==2.0.0
    exifread==3.5.1
    gunicorn==21.2.0
    importlib-metadata==6.7.0
    packaging==24.0
    pillow==9.5.0
    psycopg2-binary==2.8.6
    pytz==2021.3
    six==1.17.0
    typing-extensions==4.7.1
    zipp==3.15.0

Stage 13 — Django 2.2.28 (LTS), Python 3.9
------------------------------------------

::

    django==2.2.28
    django-grappelli==2.13.4
    django-photologue==3.10
    django-sortedm2m==2.0.0
    exifread==3.5.1
    gunicorn==21.2.0
    packaging==26.2
    pillow==9.5.0
    psycopg2-binary==2.8.6
    pytz==2026.3.post1
    six==1.17.0
    sqlparse==0.5.5

Stage 14 — Django 3.0.14, Python 3.9
------------------------------------

::

    asgiref==3.11.1
    django==3.0.14
    django-grappelli==2.14.2
    django-photologue==3.11
    django-sortedm2m==3.0.0
    exifread==3.5.1
    gunicorn==21.2.0
    packaging==26.2
    pillow==9.5.0
    psycopg2-binary==2.8.6
    pytz==2026.3.post1
    sqlparse==0.5.5
    typing-extensions==4.16.0

Stage 15 — Django 3.1.14, Python 3.9
------------------------------------

The generated runtime lock is ``requirements/production.txt``.
Issue :doc:`issues/084-django-3-1-is-the-next-runtime-upgrade`, "Checks", records its validation.

Stage 16 — Django 3.2.25 (LTS), Python 3.10
-------------------------------------------

The generated runtime lock is ``requirements/production.txt``.
Issue :doc:`issues/085-django-3-2-is-the-next-runtime-upgrade`, "Checks", records its validation.

Stage 17 — Django 4.2.30 (LTS), Python 3.12
-------------------------------------------

::

    asgiref==3.12.1
    django==4.2.30
    django-grappelli==3.0.10
    django-photologue==3.18
    django-sortedm2m==4.0.0
    exifread==3.5.1
    gunicorn==23.0.0
    packaging==26.2
    pillow==12.3.0
    psycopg2-binary==2.9.10
    sqlparse==0.5.5

Stage 18 — Django 5.2.16 (LTS), Python 3.12
-------------------------------------------

::

    asgiref==3.12.1
    django==5.2.16
    django-grappelli==4.0.4
    django-photologue==3.19
    django-sortedm2m==4.0.0
    exifread==3.5.1
    gunicorn==26.0.0
    packaging==26.2
    pillow==12.3.0
    psycopg2-binary==2.9.12
    sqlparse==0.5.5

Stage 19 — Django 6.0.7, Python 3.12
------------------------------------

::

    asgiref==3.12.1
    django==6.0.7
    django-grappelli==5.0.0
    django-photologue==3.20
    django-sortedm2m==4.0.0
    gunicorn==26.0.0
    packaging==26.2
    pillow==12.3.0
    psycopg2-binary==2.9.12
    sqlparse==0.5.5


Appendix B — a note on the working tree
=======================================

While this analysis was being produced the working copy was switched from branch
``test-coverage_g78`` to ``main`` by something outside this session. The
test-coverage work is intact on ``test-coverage_g78``, and **that branch is the
baseline this document assumes**, because it is where the current test
infrastructure lives. The two branches are not identical:

* ``requirements/testing.txt`` on ``main`` is still the pre-modernisation
  ``django-nose`` / ``nose`` / ``yeam`` stack. The pytest stack described in
  Part 1 (``pytest==3.5.0``, ``pytest-django==2.9.1``, ``coverage``, ``mock``,
  ``pbr``) only exists on ``test-coverage_g78``.
* ``ylaneenkasvit/test_settings.py`` — the settings module that Part 3 and
  Stage 5 refer to for ``TEST_NAME`` and ``SOUTH_TESTS_MIGRATE`` — exists only
  on ``test-coverage_g78``. On ``main`` there is only a three-line
  ``kasvimuseo/test_settings.py``.
* ``docs/`` (including ``test-coverage-plan.rst``) exists only on
  ``test-coverage_g78``. This file was written on ``main``, so it will need
  moving or merging.
* Three small bug fixes in ``kasvimuseo/models.py``, ``admin.py`` and
  ``views.py`` are on ``test-coverage_g78`` only.

Everything in Parts 1, 2, 4 and 5 — ``requirements/production.txt``,
``requirements/dev.txt``, ``dev/Containerfile``, ``ylaneenkasvit/common_settings.py``,
``ylaneenkasvit/urls.py`` and the ``kasvimuseo`` application modules — is
identical on both branches, so the upgrade sequence itself is unaffected.
Merge ``test-coverage_g78`` before starting Stage 0: the suite is the gate for
every stage that follows.
