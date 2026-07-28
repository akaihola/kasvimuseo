=============================================================
Issue 028: photologue <= 3.15.1 breaks on Pillow 10 and later
=============================================================

:Status: Open
:Severity: Medium
:Area: dependencies / photologue
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none -- confirmed at runtime, see below)
:Decision: undecided
:Resolution: (none yet)

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

See also
========

``docs/upgrade-plan.rst`` Part 3b.1. Issue 027 is the general form.
