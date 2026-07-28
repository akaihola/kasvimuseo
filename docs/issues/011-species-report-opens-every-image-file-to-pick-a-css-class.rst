====================================================================
Issue 011: Species report opens every image file to pick a CSS class
====================================================================

:Status: Open
:Severity: Medium
:Area: templates / operations
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templates.py (uses real JPEG fixtures for these views)
:Depends on: (none)
:Blocks: (none)
:Related: 004 -- option 2 there depends on how the species photo is rendered
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``reports/planted-species.html`` reads image dimensions in two places::

    <div class="header {% if page.species.photo.image.width > page.species.photo.image.height %}horizontal{% else %}vertical{% endif %}">
        <div class="photo"><!-- {{ page.species.photo.image.width }}x{{ page.species.photo.image.height }} -->

Reading ``.width``/``.height`` makes Django open the file. The second use is a debug
comment, but the first is a real ``horizontal``/``vertical`` class, so **removing the
comment alone does not remove the file access**.

This is the cause of the ``IOError`` the README warns about, and why
``dev/kasvimuseo media fetch`` exists: the printable and compact reports need the actual
image files present, not just a ``MEDIA_URL``.

Impact
======

Reports break with IOError when media is missing, and open every referenced image on every render when it is not.

Options
=======

1. Store the orientation on the ``Photo``/``Species`` when the image is uploaded, and
   render from that -- no file access at render time.
2. Use photologue's cached display size if it exposes one without opening the original.
3. Delete the debug comment regardless; it is redundant with the class.
