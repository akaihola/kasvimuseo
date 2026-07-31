=============================================================
Issue 028: photologue <= 3.15.1 breaks on Pillow 10 and later
=============================================================

:Status: Fixed
:Severity: Medium
:Area: dependencies / photologue
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: ``test_templates.py::test_reports_build_an_uncached_photo_size``
    pins the resize this depends on; the ``AttributeError`` itself was
    confirmed at runtime, see below
:Depends on: (none)
:Blocks: 027 -- a constraint the lock must carry
    036 -- Stages 2-16
:Related: 035 -- photologue is the package on both sides of this
:Decision: Record the bound; upgrade nothing. ``Pillow<10`` while photologue is
    2.6.1-3.15.1 (upgrade plan Stages 2-16) and ``Pillow>=9.1`` from photologue
    3.16 (Stage 17 on); 9.5.0 satisfies both and is what Stage 10 moves to.
    Written where the versions are set -- beside ``Pillow==6.2.2`` in
    ``dev/Containerfile``, beside ``django-photologue`` in
    ``requirements/production.txt``, which is the pin that implies it, and
    beside the unpinned resolution in the production ``Dockerfile`` -- and in
    ``docs/upgrade-plan.rst`` 3b.1 and Stage 10. The suite now covers it as
    well as describes it.
:Resolution: 679d96d records the bound beside every pin that sets or
    implies a Pillow version; 5d7a129 adds the test that reaches the call

Problem
=======

photologue calls ``Image.ANTIALIAS``, which Pillow removed in 10.0.0.

Read out of the sources on both sides:

=========================== =============================================
photologue                  Resampling API used
=========================== =============================================
2.6.1 (pinned) ... 3.15.1   ``Image.ANTIALIAS``
3.16 ... 3.20               ``Image.Resampling.LANCZOS``
=========================== =============================================

=========================== =============================================
Pillow                      State
=========================== =============================================
... 9.0.0                   ``ANTIALIAS`` present, no ``Resampling`` enum
9.1.0 ... 9.5.0             both present -- the overlap window
**10.0.0** ...              ``ANTIALIAS`` **removed**
=========================== =============================================

Confirmed on Pillow 12.3.0::

    >>> PIL.Image.ANTIALIAS
    AttributeError: module 'PIL.Image' has no attribute 'ANTIALIAS'

Two details matter for how this surfaces.

**Where it fails.** The call is in ``ImageModel.resize_image()``, reached from
``create_size()``, reached from ``_get_SIZE_url()`` -- the lazy accessor behind
``photo.get_display_url()``. ``kasvimuseo/photos.py`` calls that for every photo
on the species pages, so it is a 500 on page render, not on upload and not at
startup.

**When it fails.** ``create_size()`` only runs when ``size_exists()`` is false.
A developer with a warm cache directory never sees it, while production -- or
anyone who ran ``media fetch`` without the derived sizes -- breaks immediately.
No smoke test short of rendering a page with an uncached photo size catches it.

There is a second, smaller trap on the far side: photologue 3.16 declares
``Pillow>=9``, but ``Image.Resampling`` only appears in Pillow **9.1.0**. Its
own metadata is wrong by one minor version.

Impact
======

Not a problem today -- the container pins Pillow 6.2.2. It becomes one the
moment anything resolves Pillow freely, which is exactly what happens if issue
027 is addressed carelessly, and at every upgrade stage up to 16.

``Image.FLIP_LEFT_RIGHT`` and ``Image.ROTATE_180``, which photologue also uses,
are **fine** -- they still exist in Pillow 12 as module-level aliases.
``ANTIALIAS`` is the only casualty.

Options
=======

Record the constraint explicitly wherever Pillow is pinned:

* ``Pillow<10`` while photologue is 3.15.1 or older -- upgrade plan Stages 2-16
* ``Pillow>=9.1`` from photologue 3.16 -- Stages 17 onwards

Pillow **9.5.0** satisfies both sides and is the right pin for every stage up
to and including 16.

What was recorded, and where
============================

Nothing installed changed: ``dev/Containerfile`` still pins ``Pillow==6.2.2``
and ``requirements/production.txt`` still pins ``django-photologue==2.6.1``.
Three comments and two paragraphs were added, each in the place the person who
hits this will be reading:

``dev/Containerfile``
    Beside the Pillow pin, because that is the only place a version is chosen.
    It now says what the pin means -- ``Pillow<10``, not merely "the last
    release for Python 2.7" -- where the failure surfaces, and that 9.5.0 is
    the next value.

``requirements/production.txt``
    Beside ``django-photologue``, because the pin that *implies* the bound is
    there while Pillow is not mentioned at all (issue 027). A reader raising
    photologue without reading the Containerfile is exactly the person this
    catches.

``Dockerfile``
    The production image resolves photologue's dependencies instead of pinning
    them, so Pillow is chosen there by pip. Today the ``python:2.7-alpine``
    base is what holds it below 10 -- Pillow 7.0 dropped Python 2.7 -- which
    means the bound is satisfied by accident and stops being satisfied the
    moment that base moves. The comment says so.

``docs/upgrade-plan.rst``
    3b.1 and Stage 10 now record the ruling rather than the analysis.

A check, not only a comment
===========================

The claim above -- that nothing short of rendering a page with an uncached
photo size catches this -- was measured rather than repeated. Deleting
``Image.ANTIALIAS`` and running the suite fails **five** tests:

* four in the admin photo changelist, which builds ``admin_thumbnail``. That
  size crops, and photologue's crop branch resizes whatever it is handed, so
  the call is reached for any photo at all. The suite therefore did already
  cover the removal -- through the admin, and by accident.
* one on the public species report, added here.

The reports ask for ``display``, which does not crop, and the non-crop branch
returns early rather than upscale. Every photo the suite built was smaller
than that size, so the second call site -- the plain
``im.resize(new_dimensions, Image.ANTIALIAS)`` -- had never run, and the pages
the garden actually serves were covered by nothing.
``kasvimuseo/tests/test_templates.py::test_reports_build_an_uncached_photo_size``
renders the species report with a cold cache and a photo twice the ``display``
size, then asserts the cached file exists and came out scaled down. Both
branches are now covered, and the one on the public page is covered on
purpose.

What 027 has to carry
=====================

For every stage's lock: ``Pillow==9.5.0`` from Stage 10 through Stage 16 --
the value, not just the ``<10`` bound, since it is also the ceiling for
Python 3.7 -- and ``Pillow>=9.1`` from Stage 17, written by hand because
photologue 3.16's own metadata says ``>=9`` and is wrong. Before Stage 10 the
interpreter enforces it: 6.2.2 is the last Pillow for Python 2.7.

See also
========

``docs/upgrade-plan.rst`` Part 3b.1. Issue 027 is the general form.
