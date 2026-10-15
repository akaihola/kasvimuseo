=======================================================
Issue 089: A photo effect leaves a phone photo sideways
=======================================================

:Status: Accepted
:Severity: Low
:Area: photos / dependencies
:Reported: 2026-10-05
:Source: Pre-merge review of the Django 6.0 branch of issue 088
:Evidence: ``kasvimuseo/tests/test_photo_orientation.py`` --
    ``test_a_photo_with_an_effect_stays_sideways`` pins the defect, and
    ``test_a_photo_with_no_effect_is_turned_upright`` pins the path that
    works. The first test passes on photologue 3.20 and fails on 3.19.
:Depends on: (none)
:Blocks: (none)
:Related: 088 -- its move to photologue 3.20 brings this regression
    054 -- the four photo sizes, none of which has an effect
:Decision: Options 1, 3 and 4, ruled by the maintainer on 2026-10-15 when
    they accepted task 12. Option 2 is rejected. Option 1: the effect test
    keeps pinning what photologue does until upstream fixes it. Option 3:
    task 18 turns each uploaded original upright before photologue stores
    it, which also fixes the label layout that ``measure_photo_orientation``
    in ``kasvimuseo/models.py`` reads from the stored pixels. Option 4: the
    maintainer sent the report on 2026-10-15; "Upstream report" below links
    it. Task 19 proposes to remove the work-around after the upstream fix.
    The agent of task 12 had chosen options 1 and 4 on the evidence on
    2026-10-11, as ``docs/issues/README.rst`` allows; the maintainer added
    option 3 and rejected option 2.
:Resolution: (none yet) -- task 18 lands the work-around. Upstream issue 233
    is the signal for the photologue fix.

This issue is for the maintainer and the next agent who touches photos. It
decides whether the project works around a photologue 3.20 regression or
waits for an upstream fix.

Problem
=======

A phone stores an upright photo as a landscape image. An EXIF ``Orientation``
tag tells the viewer to turn it. Photologue reads that tag when it builds each
cached size, such as ``display`` and ``thumbnail``.

Photologue 3.20 applies the ``PhotoEffect`` before it reads the tag. An effect
that changes colour, brightness, contrast or sharpness, or that applies a
filter, returns a new image without EXIF data. Photologue then finds no tag
and does not turn the photo. Photologue 3.19 read the tag from the stored
original file, so the effect did not matter.

Photologue reads the effect from the photo first and then from the photo size.
Either one causes the defect.

Impact
======

Nothing is affected today. The installation had no row in
``photologue_photoeffect`` when this issue was filed, so no photo and no photo
size has an effect. The private deployment repository keeps that check.

A staff user can create an effect, because photologue's ``PhotoEffect`` admin
stays registered. ``PhotoForm`` in ``kasvimuseo/forms.py`` excludes only
``sites``, so the photo admin offers the ``effect`` field. After the user
assigns an effect, every new cached size of that photo is sideways on the
species pages, the plant list and the labels.

Options
=======

1. Accept the regression. No data triggers it. The pinning test fails when an
   upstream release fixes it, and that failure is the signal to close this
   issue.
2. Remove ``effect`` from ``PhotoForm``. Gardeners then cannot attach an effect
   to a photo. A photo size can still have one through photologue's own admin.
3. Turn each uploaded original upright before photologue stores it, for
   example with ``PIL.ImageOps.exif_transpose``. This changes the stored files
   and needs its own tests.
4. Report the regression to django-photologue. Somebody with the maintainer's
   permission must send it, because it is published under their account.

The agent recommends options 1 and 4. The ``Decision`` field records that
choice.

Upstream report
===============

The maintainer reported the regression as
`django-photologue issue 233
<https://github.com/richardbarran/django-photologue/issues/233>`_ on
2026-10-15. Before that, a throwaway Django project with SQLite checked
every claim of the report against photologue 3.19, 3.20 and master at
commit ``a8f96eb``, which includes pull request 232. 3.19 turns the photo
upright with and without an effect. 3.20 and master leave it sideways with
an effect on the photo or on the photo size. Pull request 232 fixes the
orientation map and the mirrored values, but not the order of the effect
and the tag read.

Reproduce
=========

Run the pinning tests in the Django 6.0 image::

    $ KASVIMUSEO_IMAGE=kasvimuseo-dev-issue088 dev/kasvimuseo app test \
        kasvimuseo/tests/test_photo_orientation.py

Both tests pass. In the Django 5.2 image, ``kasvimuseo-dev-issue087``, which
has photologue 3.19, the effect test fails with ``(20, 40) == (40, 20)``. That
failure shows that 3.19 turned the photo upright.
