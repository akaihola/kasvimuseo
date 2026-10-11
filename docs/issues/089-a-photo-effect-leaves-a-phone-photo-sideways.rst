=======================================================
Issue 089: A photo effect leaves a phone photo sideways
=======================================================

:Status: Deferred
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
:Decision: Options 1 and 4, decided on the evidence on 2026-10-11 by the
    agent of task 12, as ``docs/issues/README.rst`` allows when only the
    ruling is missing. The maintainer confirms or changes it when they accept
    task 12. Option 1: accept the regression and keep the pinning test, because
    no photo and no photo size has an effect, and option 3 would change every
    stored original to fix a case nobody uses. Option 2 was not taken, because
    photologue's own admin keeps the same field on a photo size, so it would
    hide the regression rather than close it. Option 4: the maintainer sends
    the report under "Upstream report" below from their own account. An agent
    cannot send it, because it is published under the maintainer's name.
:Resolution: (none yet) -- ``Deferred`` until photologue reads the tag before
    the effect again. The pinning test then fails, and the change that updates
    it closes this issue.

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

This section is for the maintainer. It holds the text of the report that
option 4 asks for. The maintainer sends it to
https://github.com/richardbarran/django-photologue/issues and then records
the issue link in the ``Resolution`` field. No report with this content was
found there on 2026-10-11.

Title: ``Photo.create_size() applies the effect before it reads the EXIF
orientation, so an effect leaves a phone photo sideways (3.20)``

.. code-block:: text

    Since 3.20, Photo.create_size() calls effect.pre_process(im) before it
    reads the EXIF Orientation tag with im.getexif(). An effect that uses
    ImageEnhance or a filter returns a new image, and that image has no EXIF
    data. create_size() then finds no Orientation tag and does not transpose
    the photo. A photo taken upright on a phone is cached sideways in every
    size.

    3.19 read the tag from the stored original, so the effect did not matter.

    To reproduce:

    1. Save a 40x20 JPEG with EXIF Orientation = 6 as a Photo.
    2. Call photo.get_display_size(). It returns (20, 40).
    3. Give the photo any PhotoEffect, for example contrast=1.2, and clear
       the cache.
    4. Call photo.get_display_size() again. It returns (40, 20).

    The same happens when the PhotoSize has the effect instead of the Photo.

    A fix is to read the Orientation tag, or to call
    ImageOps.exif_transpose(), before the effect's pre_process() runs.

    A test that pins both cases is in
    kasvimuseo/tests/test_photo_orientation.py of
    https://github.com/akaihola/kasvimuseo.

Reproduce
=========

Run the pinning tests in the Django 6.0 image::

    $ KASVIMUSEO_IMAGE=kasvimuseo-dev-issue088 dev/kasvimuseo app test \
        kasvimuseo/tests/test_photo_orientation.py

Both tests pass. In the Django 5.2 image, ``kasvimuseo-dev-issue087``, which
has photologue 3.19, the effect test fails with ``(20, 40) == (40, 20)``. That
failure shows that 3.19 turned the photo upright.
