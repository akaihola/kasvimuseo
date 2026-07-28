=========================================================
 Dependency and platform upgrade plan: Django 1.5 → 6.0
=========================================================

:Status: analysis and plan, nothing implemented
:Date: 2026-07-28
:Scope: every Python dependency of ``ylaneenkasvit``/``kasvimuseo``, the
        Python runtime itself, and the code changes each step forces

.. contents::
   :depth: 2
   :local:


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
034                 Part 6, "The admin-list fork is the real cost"
035                 Parts 2.2 and 2.3, the grappelli and photologue ladders
036                 Part 4, the whole staged sequence
=================== ===========================================================

Issue ``016``, filed by the test coverage work, is the other Python 3 landmine
and is a prerequisite of Stage 10.


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
``django``                   1.5.1     1.5.12 is the last 1.5 patch release
``django-photologue``        2.6.1     Owns database schema. The hard pacer.
``django-grappelli``         2.4.5     Admin skin. The other hard pacer.
``django-extensions``        1.5.9     In ``INSTALLED_APPS``; nothing imports it
``django-indexer``           0.3.0     **Zero references anywhere**
``django-paging``            0.2.4     **Zero references anywhere**
``django-jqm``               1.1.0.2   ``akaihola`` fork, installed from GitHub
``gunicorn``                 0.17.4    Also (pointlessly) in ``INSTALLED_APPS``
``psycopg2-binary``          2.8.4     ``2.8.6`` is the last 2.8 patch
``six``                      1.11.0    Nothing in this repo imports it
``south``                    0.8.1     Pre-1.7 migrations. Dies at Django 1.7.
============================ ========= =========================================

Plus, installed by ``dev/Containerfile`` with ``--no-deps`` and therefore
*invisible to* ``production.txt``:

* ``Pillow==6.2.2`` — photologue's imaging backend (the last Pillow that runs on
  Python 2.7)
* ``django-sortedm2m==1.5.0`` — not actually needed by photologue 2.6.1; it
  becomes a real dependency at photologue 2.8.

None of the pinned production releases declare ``install_requires`` on PyPI, so
the *declared* dependency tree is completely flat. The real tree is implicit —
which is exactly why ``--no-deps`` plus hand-picked extras is currently needed.

Test and development
--------------------

``requirements/testing.txt``
    ``pytest==3.5.0``, ``pytest-django==2.9.1``, ``coverage==4.5.4``,
    ``mock==2.0.0``, ``pbr==4.0.2``.
    pytest 3.5.0 pulls ``py``, ``six``, ``attrs``, ``more-itertools``,
    ``pluggy<0.7``, ``funcsigs``, ``setuptools``.

``requirements/dev.txt``
    ``django-extensions==1.5.9``, ``flax`` (``akaihola`` fork, GitHub),
    ``django-pserver``, ``Fabric==1.6.0``, ``Werkzeug==0.8.3``.

``requirements/integration-tests.txt``
    ``pytest==4.6.9``, ``selenium==3.141.0``, ``pytest-selenium==1.17.0``,
    ``pytest-html==1.22.1``, ``pytest-metadata``, ``pytest-variables``,
    ``pytest-base-url``, ``podman-compose`` — plus eleven pins
    (``atomicwrites``, ``configparser``, ``contextlib2``, ``funcsigs``,
    ``importlib-metadata``, ``more-itertools``, ``pathlib2``, ``py``,
    ``scandir``, ``wcwidth``, ``zipp``) that exist **only** to keep pytest 4.6.9
    alive on Python 2.7. All eleven disappear the day Python 3 lands.


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

Note the comment in ``requirements/testing.txt`` — "pytest-django 2.9.1 is the
last release supporting Django 1.5" — is correct, but it is *also* the case
that 2.9.1 keeps working all the way to **Django 1.9**. The test suite does not
need touching until then.

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

psycopg2 2.9 stopped forcing the session to UTC, so with ``USE_TZ = True``
(which this project sets) that assertion fires. Django 3.1 replaced it with
``def tzinfo_factory(self, offset): return self.timezone``. Therefore:

    **psycopg2-binary must stay < 2.9 until Django ≥ 3.1.**

``psycopg2-binary`` availability: 2.7.7 (py2.6+), 2.8.6 (py2.7 – 3.8),
2.9.x (py3.6+, latest 2.9.12 requires 3.9+).

2.6 Everything else
-------------------

============================ =========================================================
Package                      Ladder
============================ =========================================================
``django-sortedm2m``         1.1.1 (Dj 1.5–1.8) → 1.5.0 (–1.9) → 2.0.0 (1.11–2.2)
                             → 3.0.0 (2.2–3.0) → 3.1.1 (2.2–3.2) → 4.0.0 (4.2–5.1)
``Pillow``                   6.2.2 last on py2.7 · 7.0 needs 3.5 · 9.0 → 3.7 ·
                             10.0 → 3.8 · 12.0 → 3.10. **Also capped from above
                             by photologue** — ``<10`` up to photologue 3.15.1,
                             ``>=9.1`` from 3.16. See 3b.1; 9.5.0 satisfies both.
``ExifRead``                 2.1.2+ needed by photologue 3.4–3.19; 3.x needs py≥3.7;
                             not needed at all from photologue 3.20. API stable
                             throughout — see 3b.4.
``django-model-utils``       needed only by photologue 2.8 – 3.1
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
                             2.x/3.x are a rewrite with a different API
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
``django.conf.urls.defaults``                        **1.6**  ``ylaneenkasvit/urls.py``, ``kasvimuseo/urls.py``
``DATABASES[...]['TEST_NAME']``                      1.8      ``ylaneenkasvit/test_settings.py``
``django.contrib.admin.util``                        1.9      ``kasvimuseo/templatetags/kasvimuseo_admin_list.py``
``EMPTY_CHANGELIST_VALUE``                           1.9      ``kasvimuseo_admin_list.py``
``django.db.models.get_model``                       1.9      —
``SubfieldBase``                                     1.10     —
``django.core.context_processors``                   1.10     ``ylaneenkasvit/common_settings.py`` (5 entries)
``TEMPLATE_DIRS`` / ``TEMPLATE_CONTEXT_PROCESSORS``  1.10     ``common_settings.py``
string view names in ``url()``                       1.10     ``ylaneenkasvit/urls.py`` (3)
``patterns()``                                       **2.0**  ``ylaneenkasvit/urls.py``, ``kasvimuseo/urls.py``
``django.core.urlresolvers``                         2.0      ``kasvimuseo/admin.py``, ``ylaneenkasvit/dashboard.py``
``force_unicode``                                    2.0      ``kasvimuseo_admin_list.py``
``MIDDLEWARE_CLASSES`` (and its default)             2.0      **nothing — see below**
``ForeignKey`` without ``on_delete``                 2.0      ``kasvimuseo/models.py`` (13 sites)
``django.contrib.auth.views.login`` / ``logout``     2.1      ``ylaneenkasvit/urls.py``
``django.utils.six``                                 3.0      —
``render_to_response``                               3.0      ``kasvimuseo/views.py``
``postgresql_psycopg2`` ENGINE alias                 3.0      ``common_settings.py``
``ugettext`` / ``ugettext_lazy``                     **4.0**  ``models.py``, ``admin.py``, ``dashboard.py``
``force_text`` / ``smart_text``                      4.0      ``kasvimuseo_admin_list.py``
``DEFAULT_FILE_STORAGE`` / ``STATICFILES_STORAGE``   5.1      — (set ``STORAGES`` from 4.2)
``index_together``                                   5.1      —
==================================================== ======== =====================================================

Two settings landmines that a grep does not show, because the settings are
*missing*:

**No MIDDLEWARE at all.** ``common_settings.py`` never defines
``MIDDLEWARE_CLASSES`` or ``MIDDLEWARE``; the site runs on the
``global_settings`` default. Django 1.10 introduced ``MIDDLEWARE`` with a default
of ``None`` and Django **2.0 deleted** ``MIDDLEWARE_CLASSES`` and made
``MIDDLEWARE`` default to ``[]``. At Django 2.0 the site will therefore run with
*no middleware whatsoever* — no sessions, no auth, no CSRF, no admin — and it
will not raise an obvious error. Define ``MIDDLEWARE`` explicitly **now**, while
it is still just a no-op restatement of the current default.

**No** ``django.contrib.messages`` **app.** Its context processor is configured
but the app is not in ``INSTALLED_APPS``. The admin requires it from Django 1.7
onwards. Add it in Stage 0.

Python 2 → 3 code work (Stage 10)
---------------------------------

* ``__unicode__`` on 12 model/class definitions → ``__str__``
* ``unicode(...)`` at 3 sites
* ``force_unicode`` / ``smart_str`` → ``force_text`` / ``smart_text``
* ``kasvimuseo/forms.py``: ``remove_diacritics`` is
  ``filter(lambda x: not combining(x), normalize('NFKD', u))``. On Python 2 that
  returns a string; on Python 3 it returns an iterator, and ``slugify()`` will
  receive ``<filter object …>``. This is a **silent** data corruption bug, not a
  crash. Must become ``''.join(...)``.
* ``common_settings.py`` hardcodes
  ``here('..', 'lib', 'python2.7', 'site-packages', 'photologue', 'templates')``
  in ``TEMPLATE_DIRS``. Remove it — ``APP_DIRS`` finds photologue's templates.
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
pins.** The existing ``dev/Containerfile`` already does this by hand, with
``pip install --no-deps`` plus two manually chosen extras, and a comment
explaining that it "avoids photologue dragging in an incompatible Pillow" —
this analysis is that comment, generalised and made explicit.

The mechanism to adopt is ``uv pip compile``: keep a short ``*.in`` per stage
with the direct pins and the upper bounds established above, and commit the
generated fully-pinned ``*.txt``. `Appendix A — Resolved lock set per stage`_
gives the output for every stage that could be resolved.


Part 4 — The upgrade sequence
=============================

Each stage should end green on the test suite and on a **restored production
dump**, not on an empty database — most of the risk here is schema and data, not
imports.

Stage 0 — Dead weight and defensive settings (no version changes)
-----------------------------------------------------------------

Cheap, zero-risk, and it shortens every later stage.

#. Remove ``django-indexer`` and ``django-paging`` from ``production.txt`` and
   ``INSTALLED_APPS``. Nothing in the repo references ``indexer`` or ``paging``
   in any ``.py``, ``.html`` or template. They are vestigial Sentry
   dependencies.
#. Remove ``'gunicorn'`` from ``INSTALLED_APPS``. It was only ever there for the
   ``run_gunicorn`` management command, which gunicorn deleted in 19.7.1.
   Gunicorn itself stays as the WSGI server.
#. Add ``'django.contrib.messages'`` to ``INSTALLED_APPS``.
#. Add an explicit ``MIDDLEWARE_CLASSES`` equal to today's effective default.
#. Delete the dead ``/media/grappelli/`` URL pattern in ``ylaneenkasvit/urls.py``.
   It serves ``os.path.dirname(grappelli.__file__)/media``, and grappelli 2.4.5
   has no ``media/`` directory — verified by listing its sdist. Delete
   ``ADMIN_MEDIA_PREFIX`` too; Django dropped it in 1.4.
#. Vendor ``django-jqm`` into the repo. It is seven templates, two static files
   and three near-empty modules, from a personal fork installed off a GitHub
   URL. Vendoring removes a network dependency from every build and makes the
   Django-version fixes to those templates ordinary in-repo edits.
#. Move ``django-extensions`` out of ``production.txt`` into ``dev.txt`` only
   (it is already listed in both) and out of the production ``INSTALLED_APPS``.

Stage 1 — Django 1.5.1 → 1.5.12
-------------------------------

Security patches only, no API change. Free.

Stage 2 — Photologue 2.6.1 → 2.8.3, still on Django 1.5
--------------------------------------------------------

Photologue moves *first* and alone, because it owns tables.

* ``2.7``: prefixes every setting with ``PHOTOLOGUE_``. This project sets none,
  so it is a no-op.
* ``2.8``: the expensive one.

  - ``Photo.title_slug`` becomes ``Photo.slug``. ``kasvimuseo/forms.py``
    manipulates ``self.fields['title_slug']`` and will raise ``KeyError``.
    (2.8 keeps a ``title_slug`` *property* that warns, but the form field is
    gone.)
  - ``Photo`` and ``Gallery`` gain a ``sites`` M2M → add
    ``'django.contrib.sites'`` to ``INSTALLED_APPS`` and set ``SITE_ID``.
    Neither exists in the project today.
  - New dependencies: ``django-sortedm2m`` (1.1.1+) and ``django-model-utils``.
  - Run photologue's South migrations. **This requires dropping**
    ``SOUTH_MIGRATION_MODULES`` and ``ylaneenkasvit/external_migrations/photologue/``,
    which currently override photologue's migration history with a single local
    squashed ``0001_initial``. Fake photologue back to its own ``0001`` and then
    migrate forward.

Stage 3 — Django 1.5.12 → 1.6.11
--------------------------------

* **Blocker:** ``django.conf.urls.defaults`` is gone. Both ``urls.py`` files
  must import from ``django.conf.urls``.
* ``south`` 0.8.1 → 1.0.2 (South's last release; it supports 1.6, never 1.7).
* ``django-grappelli`` 2.4.5 → 2.5.7.
* ``django-extensions`` 1.5.9 → 1.6.7.

Stage 4 — Photologue 2.8.3 → 3.0.2, still on Django 1.6
--------------------------------------------------------

The single most important ordering constraint in this document. Photologue 3.0.x
and 3.1.1 are the only releases carrying both ``south_migrations/`` and
``migrations/``; 3.2 drops the South set. Land 3.0.2 (or 3.1.1) on Django 1.6
*while South still works*, so that the schema matches what photologue's Django
``0001_initial`` expects when Django 1.7 takes South away. Getting this wrong —
i.e. arriving at Django 1.7 with a 2.x-era photologue schema and no South —
means hand-writing the delta as a fake migration against production.

Stage 5 — Django 1.6.11 → 1.7.11: the South cut
-----------------------------------------------

* Delete ``south`` from every requirements file and from ``INSTALLED_APPS``.
* Delete ``SOUTH_MIGRATION_MODULES`` and ``SOUTH_TESTS_MIGRATE``
  (``test_settings.py`` currently disables South migrations for exactly this
  ordering problem — the workaround goes away with the cause).
* Delete ``from south.modelsinspector import add_introspection_rules`` and its
  two call sites in ``kasvimuseo/models.py``.
* Replace the 19 South migrations in ``kasvimuseo/migrations/`` with a fresh
  Django ``0001_initial``; on production run ``migrate --fake-initial``.
  All 19 are ``orm[...]``-style South migrations, so none of them are portable.
  Exactly two are data migrations — ``0011_extract_lighting`` and
  ``0018_move_variety_to_cultivation_history`` — and their *effects* are already
  in the production data, so they do not need re-running; only the schema has to
  match.
* ``photologue`` switches to its own ``migrations/``; fake it to the matching
  point.
* ``DATABASES['default']['TEST_NAME']`` → ``'TEST': {'NAME': …}`` in
  ``test_settings.py`` (the new form works from 1.7; the old one is deleted
  in 1.8).
* ``django-grappelli`` → 2.6.5.
* ``pytest-django`` 2.9.1 still works — do not touch the test stack yet.

Stage 6 — Django 1.7.11 → 1.8.19 (LTS)
--------------------------------------

* ``TEMPLATE_DIRS`` / ``TEMPLATE_CONTEXT_PROCESSORS`` / ``TEMPLATE_DEBUG`` →
  a single ``TEMPLATES`` setting with ``APP_DIRS = True``. This is also where
  the hardcoded ``lib/python2.7/site-packages/photologue/templates`` path
  disappears — a prerequisite for Stage 10.
* ``django.core.context_processors`` → ``django.template.context_processors``.
* ``django.contrib.admin.util`` → ``django.contrib.admin.utils`` in
  ``kasvimuseo_admin_list.py``.
* ``django-grappelli`` → 2.7.3.
* ``django-photologue`` → 3.4.1. This removes tagging (3.2) and drops
  ``django-model-utils`` (3.2). ``ExifRead`` becomes a dependency (3.4).
* ``django-extensions`` → 1.7.9.

Stage 7 — Django 1.8.19 → 1.9.13
--------------------------------

* ``EMPTY_CHANGELIST_VALUE`` is gone → ``cl.model_admin.get_empty_value_display()``
  in ``kasvimuseo_admin_list.py``.
* ``django.contrib.admin.util`` is gone (already handled in Stage 6).
* ``ForeignKey(on_delete=...)`` starts warning. Add it now — it becomes
  mandatory at 2.0 and adding it early costs one no-op migration.
* **Test stack moves for the first time:** ``pytest-django`` 2.9.1 → 3.1.2
  (Django 1.7–1.10), ``pytest`` 3.5.0 → 3.0.x/3.10.x.
* ``django-grappelli`` → 2.8.3; ``django-photologue`` → 3.5.1 or 3.6.

Stage 8 — Django 1.9.13 → 1.10.8
--------------------------------

* ``TEMPLATE_*`` and ``django.core.context_processors`` are gone (Stage 6 already
  did this).
* Define ``MIDDLEWARE`` (new style). ``MIDDLEWARE_CLASSES`` is still honoured
  here, so both can coexist for one stage.
* String view references in ``url()`` are gone → import
  ``django.views.static.serve`` and the auth views as callables in
  ``ylaneenkasvit/urls.py``.
* ``django.core.urlresolvers`` → ``django.urls`` (available from 1.10).
* ``django-grappelli`` → 2.9.1; ``django-photologue`` → 3.6.

Stage 9 — Django 1.10.8 → 1.11.29 (LTS) — the staging point
-----------------------------------------------------------

This is where the project should sit until it is fully Python-3 clean.

* ``django-grappelli`` → 2.10.4.
* ``django-photologue`` → 3.7 (needs ``django-sortedm2m >= 1.3.3``).
* ``django-extensions`` → 2.2.9 (the last release supporting both Python 2.7
  and Django 1.11).
* ``pytest-django`` → 3.10.0, ``pytest`` → 4.6.11 (both the last with Python 2.7).
* Switch ``ylaneenkasvit/urls.py`` from ``auth.views.login``/``logout`` to
  ``LoginView``/``LogoutView`` — they arrive in 1.11 and the function views are
  deleted in 2.1, so do it while both exist.

Stage 10 — **Python 2.7 → 3.7**, staying on Django 1.11.29
-----------------------------------------------------------

The one irreversible step. Nothing else changes version in this stage.

Do the source work first, keeping the code running on 2.7 (``six`` and
``python_2_unicode_compatible`` are the tools; both are still available in
Django 1.11):

* ``__unicode__`` → ``__str__`` (12 sites)
* ``unicode(...)`` → ``str(...)`` (3 sites)
* the ``filter()`` bug in ``kasvimuseo/forms.py`` (see Part 3)
* ``force_unicode``/``smart_str`` → ``force_text``/``smart_text``

Then flip the base image ``python:2.7-alpine`` → ``python:3.7-alpine`` and the
ceiling versions:

* ``Pillow`` 6.2.2 → **9.5.0** — the highest that still has ``Image.ANTIALIAS``,
  which photologue needs until 3.16 (3b.1), and the highest that supports
  Python 3.7
* ``psycopg2-binary`` stays 2.8.6 (still the ceiling until Django 3.1)
* ``gunicorn`` → **21.2.0**, skipping 19.x and 20.x entirely. It needs only
  Python ≥3.5, is independent of Django, and is the first release free of
  ``pkg_resources`` (3b.2). Sitting on gunicorn 20 buys nothing and costs a
  ``setuptools<82`` constraint for the next eight stages.
* ``selenium`` 3.141.0 → 4.x, ``Fabric`` 1.6 → 3.x *or* delete both (see Part 5)

The full resolved lock for this stage — and every stage after it — is in
`Appendix A — Resolved lock set per stage`_.

And delete: ``six``, ``mock``, ``pbr``, ``funcsigs``, and the eleven Python-2
backports in ``integration-tests.txt``.

Why 3.7 and not 3.6: Django 1.11 supports 3.4–3.7 and 3.7 is the highest, which
minimises the number of Python bumps still to come. Pin Django ≥ **1.11.17** —
that is the exact release that added Python 3.7 support ("Django 1.11.17 fixes
several bugs in 1.11.16 and adds compatibility with Python 3.7", and it is the
first 1.11 whose ``setup.py`` carries the ``Python :: 3.7`` classifier).
Stage 9 already lands on 1.11.29, so this is satisfied.

Stage 11 — Django 1.11 → 2.0.13
-------------------------------

* ``patterns()`` gone → plain lists of ``url()``.
* ``django.core.urlresolvers`` gone (Stage 8 handled it).
* ``force_unicode`` gone (Stage 10 handled it).
* ``on_delete`` now **mandatory** on all 13 ``ForeignKey`` definitions.
* ``MIDDLEWARE_CLASSES`` gone — ``MIDDLEWARE`` must be defined (Stage 8).
* ``django-grappelli`` → 2.11.2; ``django-photologue`` → 3.8.1
  (needs ``django-sortedm2m >= 1.5.0``); ``pytest-django`` → 3.4.8.

Stage 12 — Django 2.0 → 2.1.15
------------------------------

* ``django.contrib.auth.views.login``/``logout`` deleted (Stage 9 handled it).
* ``django-grappelli`` → 2.12.4; ``django-photologue`` → 3.9.
* Python ≥ 3.5.

Stage 13 — Django 2.1 → 2.2.28 (LTS)
------------------------------------

* ``django-grappelli`` → 2.13.4; ``django-photologue`` → 3.10;
  ``django-sortedm2m`` → 2.0.0; ``pytest-django`` → 3.10.0 or 4.5.2.
* Bump Python 3.7 → 3.9 here (Django 2.2 supports 3.5–3.9). Do it as a separate
  commit from the Django bump.

Stage 14 — Django 2.2 → 3.0.14
------------------------------

* ``render_to_response`` gone → ``render(request, …)`` in ``kasvimuseo/views.py``
  (3 call sites; the ``RequestContext`` import goes with it).
* ``ENGINE`` ``django.db.backends.postgresql_psycopg2`` gone →
  ``django.db.backends.postgresql``.
* ``django.utils.six`` gone — nothing here imports it, but check that no
  remaining third-party package does.
* ``django-photologue`` → 3.11 (**Python 3 only**, ``django-sortedm2m >= 3.0.0``,
  ``Pillow >= 6``); ``django-grappelli`` → 2.14.2.
* ``psycopg2-binary`` **still < 2.9** — this is the last version where the
  ``utc_tzinfo_factory`` assertion exists.

Stage 15 — Django 3.0 → 3.1.14
------------------------------

* The ``tzinfo_factory`` fix lands → ``psycopg2-binary`` 2.9.x becomes safe.
* ``django-grappelli`` → 2.14.4; ``django-photologue`` → 3.13.

Stage 16 — Django 3.1 → 3.2.25 (LTS)
------------------------------------

* Set ``DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'`` explicitly.
  It is new in 3.2 and the default flips to ``BigAutoField`` in **6.0**;
  pinning it now prevents a surprise table rewrite four stages later.
* ``django-grappelli`` → 2.15.7; ``django-photologue`` → 3.14
  (``django-sortedm2m >= 3.1.1``); ``django-extensions`` → 3.1.5;
  ``pytest-django`` → 4.5.2; Python → 3.9/3.10.

Stage 17 — Django 3.2 → 4.0.10 → 4.1.13 → 4.2.30 (LTS)
-------------------------------------------------------

* **4.0 removes** ``ugettext_lazy`` → ``gettext_lazy`` and
  ``force_text``/``smart_text`` → ``force_str``/``smart_str``. Eight sites
  across ``models.py``, ``admin.py``, ``dashboard.py``,
  ``kasvimuseo_admin_list.py``.
* ``pytz`` leaves the tree (Django 4.0 switched to ``zoneinfo``).
* Python ≥ 3.8; at 4.2 the window is 3.8–3.12.
* ``django-grappelli`` → 3.0.x (one series covers 4.0 → 4.2);
  ``django-photologue`` → 3.15.1 (4.0), 3.16 (4.1/4.2), 3.18 (4.2);
  ``django-extensions`` → 3.2.3 / 4.x; ``pytest-django`` → 4.6+.
* At 4.2: replace ``DEFAULT_FILE_STORAGE``/``STATICFILES_STORAGE`` with
  ``STORAGES`` (removed outright in 5.1), and consider swapping
  ``psycopg2-binary`` for ``psycopg[binary]`` — psycopg 3 is supported from 4.2.

Stage 18 — Django 4.2 → 5.0.14 → 5.1.15 → 5.2.16 (LTS)
-------------------------------------------------------

* Python ≥ 3.10.
* 5.1 removes ``DEFAULT_FILE_STORAGE``, ``STATICFILES_STORAGE`` and
  ``index_together``.
* ``USE_TZ`` default becomes ``True`` in 5.0 — already set explicitly, no change.
* ``django-grappelli`` → 4.0.4; ``django-photologue`` → 3.18
  (``django-sortedm2m >= 4.0.0``, ``Pillow >= 10``); ``pytest-django`` → 4.11.1.

Stage 19 — Django 5.2 → 6.0.7 (current)
---------------------------------------

* Python ≥ 3.12.
* ``DEFAULT_AUTO_FIELD`` default flips to ``BigAutoField`` — keep the explicit
  ``AutoField`` pin from Stage 16, or plan the ``ALTER TABLE`` deliberately.
* ``psycopg2 >= 2.9.9`` or psycopg 3.
* ``django-grappelli`` → 5.0.0; ``django-photologue`` → 3.20
  (``Django >=5.2,<6.1``, ``Pillow >= 12``, **ExifRead dropped**).
* ``django-extensions`` 4.1 declares Django 4.2/5.1/5.2 and does **not** yet
  claim 6.0. Since Stage 0 already moved it to development-only, this is not a
  blocker — but do not put it back into production.


Part 5 — Packages that stop being needed
========================================

=================================== ========= ==================================================
Package                             Dies at   Because
=================================== ========= ==================================================
``django-indexer``                  Stage 0   Never referenced
``django-paging``                   Stage 0   Never referenced
``django-pserver``                  Stage 0   Only ever in a commented-out line
``gunicorn`` as an *app*            Stage 0   ``run_gunicorn`` removed in gunicorn 19.7.1
``django-jqm`` as a *dependency*    Stage 0   Vendored into the repo
``south``                           Stage 5   Django 1.7 ships migrations
``django-model-utils``              Stage 6   Photologue 3.2: "Django can now natively chain
                                              custom manager filters"
``django-tagging`` shim             Stage 6   Photologue 3.2 removed tagging
``six``                             Stage 10  Python 3 only
``mock`` + ``pbr``                  Stage 10  ``unittest.mock`` since Python 3.3
Python 2 backports [1]_             Stage 10  Pinned only to keep pytest 4.6.9 on Python 2.7
``Fabric`` + ``flax``               Stage 10  Fabric 1.x is Python 2 only, and
                                              ``ansible/install.yaml`` already does the job —
                                              delete rather than port to Fabric 3
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

The admin-list fork is the real cost
------------------------------------

``kasvimuseo/templatetags/kasvimuseo_admin_list.py`` (235 lines) is a
copy-and-modify fork of Django's own
``django/contrib/admin/templatetags/admin_list.py``. It imports six private
admin symbols and reimplements ``result_headers``, ``items_for_result`` and
``results``. Django's originals change in almost every release, so this file
must be **re-synced at every single Django stage** — nineteen times. That is
plausibly more work than all the other code changes combined.

Its only actual purpose is to put the field name into each ``<td class="...">``.
Strongly consider retiring it: either re-derive it once from Django 6.0's
source at the end, or replace it entirely with ``list_display`` callables that
return ``format_html``-wrapped markup, which needs no private API at all.
Decide this before Stage 6, not after.

Schema work needs production data
---------------------------------

Six stages touch the database (2, 4, 5, 6, 11, 16/19). ``dev/kasvimuseo db
fetch`` + ``db restore`` exists precisely for this — every schema stage should
be rehearsed on a restored production dump. Bootstrapping from migrations alone
will not surface the interesting failures (duplicate slugs after the
``title_slug`` → ``slug`` rename, ``NULL`` sites rows, orphaned photo files).

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

Two security questions, independent of the upgrade
---------------------------------------------------

Both concern ``ylaneenkasvit_settings.py``, which the upgrade will touch
repeatedly, so they are worth deciding first: the committed production
``SECRET_KEY`` and database password (``docs/issues/025``), and the fact that
``ALLOWED_HOSTS`` is set nowhere in the repository at all
(``docs/issues/026``) — which, given that Django 1.5 rejects every request when
it is empty and ``DEBUG`` is off, means production is relying on something this
repository does not contain.

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
#. The recurring ``kasvimuseo_admin_list.py`` re-sync across all nineteen stages
#. Everything else, which is largely mechanical import rewrites


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
--no-deps`` against a hand-maintained pin list.

The test stack
--------------

``testing.txt`` moves on its own schedule, driven by pytest-django (Part 2.4).
The direct pins per stage:

========== ============ ================= ========== ==========
Stage      Django       pytest-django     pytest     coverage
========== ============ ================= ========== ==========
0 – 6      1.5 – 1.8    2.9.1             3.5.0      4.5.4
7          1.9          2.9.1             3.5.0      5.5
8          1.10         3.1.2             3.10.1     5.5
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

::

    django-grappelli==2.10.4
    django-photologue==3.7
    django-sortedm2m==1.3.3
    django==1.11.29
    exifread==3.5.1
    gunicorn==21.2.0
    importlib-metadata==6.7.0
    packaging==24.0
    pillow==9.5.0
    psycopg2-binary==2.8.6
    pytz==2021.3
    typing-extensions==4.7.1
    zipp==3.15.0

``django-sortedm2m==1.3.3`` is pinned by hand — it is sdist-only and modern setuptools cannot
build it, so a resolver cannot select it (see 3b.3), but photologue's floor for
this stage requires it.

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

::

    asgiref==3.11.1
    django==3.1.14
    django-grappelli==2.14.4
    django-photologue==3.13
    django-sortedm2m==3.0.2
    exifread==3.5.1
    gunicorn==21.2.0
    packaging==26.2
    pillow==9.5.0
    psycopg2-binary==2.9.5
    pytz==2026.3.post1
    sqlparse==0.5.5
    typing-extensions==4.16.0

Stage 16 — Django 3.2.25 (LTS), Python 3.10
-------------------------------------------

::

    asgiref==3.12.1
    django==3.2.25
    django-grappelli==2.15.7
    django-photologue==3.14
    django-sortedm2m==3.1.1
    exifread==3.5.1
    gunicorn==21.2.0
    packaging==26.2
    pillow==9.5.0
    psycopg2-binary==2.9.9
    pytz==2026.3.post1
    sqlparse==0.5.5
    typing-extensions==4.16.0

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
``test-coverage_g78`` to ``master`` by something outside this session. The
test-coverage work is intact on ``test-coverage_g78``, and **that branch is the
baseline this document assumes**, because it is where the current test
infrastructure lives. The two branches are not identical:

* ``requirements/testing.txt`` on ``master`` is still the pre-modernisation
  ``django-nose`` / ``nose`` / ``yeam`` stack. The pytest stack described in
  Part 1 (``pytest==3.5.0``, ``pytest-django==2.9.1``, ``coverage``, ``mock``,
  ``pbr``) only exists on ``test-coverage_g78``.
* ``ylaneenkasvit/test_settings.py`` — the settings module that Part 3 and
  Stage 5 refer to for ``TEST_NAME`` and ``SOUTH_TESTS_MIGRATE`` — exists only
  on ``test-coverage_g78``. On ``master`` there is only a three-line
  ``kasvimuseo/test_settings.py``.
* ``docs/`` (including ``test-coverage-plan.rst``) exists only on
  ``test-coverage_g78``. This file was written on ``master``, so it will need
  moving or merging.
* Three small bug fixes in ``kasvimuseo/models.py``, ``admin.py`` and
  ``views.py`` are on ``test-coverage_g78`` only.

Everything in Parts 1, 2, 4 and 5 — ``requirements/production.txt``,
``requirements/dev.txt``, ``requirements/integration-tests.txt``,
``dev/Containerfile``, ``ylaneenkasvit/common_settings.py``,
``ylaneenkasvit/urls.py`` and the ``kasvimuseo`` application modules — is
identical on both branches, so the upgrade sequence itself is unaffected.
Merge ``test-coverage_g78`` before starting Stage 0: the suite is the gate for
every stage that follows.
