==================================================================
Issue 037: No in-UI instructions for managing plant photos
==================================================================

:Status: Open
:Severity: Medium
:Area: admin / usability
:Reported: 2026-07-28
:Source: Review of the photo management design
:Evidence: (none -- the missing text is documentation, not behaviour)
:Depends on: 002, 003 -- what the auto-attach receiver does is what there is to document
    039 -- option 3 cannot be written honestly until this is decided
    042 -- the missing capability behind the missing instructions
:Blocks: (none)
:Related: 017 -- the label editor has no browser test either
    047 -- the print toggle these instructions describe by its appearance
:Decision: undecided
:Resolution: (none yet)

Problem
=======

Nothing in the running application tells the user how plant photos are managed. The
rules exist only in the source code, and a maintainer has to read three files to
reconstruct them:

* ``kasvimuseo/forms.py`` -- ``PhotoForm.clean()`` makes ``title`` optional and derives
  it from the uploaded **filename** with the ``jpg``/``jpeg``/``jpe`` extension removed.
* ``kasvimuseo/models.py`` -- ``autoconnect_photo_to_species`` takes the **first word**
  of that title, lowercases it, and attaches the photo to the ``Species`` whose
  ``name_fi`` matches *and which has no photo yet*.
* ``kasvimuseo/photos.py`` and the Vue editor in
  ``kasvimuseo/templates/kasvimuseo/reports/planting-labels.html`` -- all photos whose
  title starts with the same word are offered as alternatives on a label, chosen with
  two unlabelled chevron buttons (``&#x2329;`` / ``&#x232a;``) that appear only when
  there is more than one candidate.

So the single most important rule -- *name the file after the Finnish species name, or
the photo attaches to nothing* -- is never stated to the person doing the uploading. The
Photologue upload form shows a ``Title`` field with no hint that leaving it blank is the
normal path, and no hint that its first word is the species key.

The other three operations are worse than undocumented; the UI actively misleads:

Removing a photo
    ``Species.photo`` is absent from ``SpeciesAdmin.fieldsets``
    (``kasvimuseo/admin.py``), so a species' photo cannot be detached from the species
    page. The read-only ``photo_image`` column shows a filename the user cannot change.
    The only route is deleting the ``Photo`` object itself, which also deletes the image
    file for every other use of it.

Replacing a photo
    Uploading a better photo under the same name does *not* replace anything: the
    auto-attach signal skips any species that already has a photo, so the new file
    becomes a silent alternative and the old one stays primary.

Choosing the primary photo
    The chevrons in the label editor write ``Label.photo``, not ``Species.photo``, and
    the read path never looks at ``Label.photo`` again -- see issue 039 -- so the choice
    is lost on the next load. There is no control anywhere for ``Species.photo``, which
    is the value everything actually renders from. Nothing in the interface distinguishes
    "the photo for this species" from "the photo on this label", and the one control that
    looks like it chooses does neither.

Impact
======

A user who is not the author cannot upload, remove, replace or re-select a plant photo
without reading the source. Photos that fail to attach fail silently, and the photo
chooser looks like it works, so the reports print the wrong plant picture with no
indication that anything went wrong.

Options
=======

1. **Help text where the decision is made.** Add ``help_text`` to the ``PhotoForm``
   ``image`` and ``title`` fields stating the filename convention and what happens if it
   is not followed, and a short intro paragraph on the Photologue add-photo page. This is
   the cheapest change and covers the case that fails most often.
2. **Make the primary photo editable.** Put ``photo`` into ``SpeciesAdmin.fieldsets`` as
   a plain choice among the species' candidate photos, so removing and replacing are
   ordinary edits rather than side effects of the signal. Then the help text has
   something true to point at.
3. **Label the label editor.** Give the chevron buttons ``title``/``aria-label`` text and
   put one line above the sheet saying what the choice applies to. The buttons are
   currently glyphs with no accessible name. What the line should say depends on issue
   039: today the honest wording is "the choice is not kept".
4. **One place to link to.** A short "Kasvikuvat" page in the admin, linked from both the
   photo list and the label editor, describing upload, remove, replace and select in four
   paragraphs -- worth it only if 1--3 are not enough on their own.

Option 1 is text-only and independent of everything else on this list. Option 2 is a
behaviour change and interacts with issues 002 and 003, which are about the same
auto-attach signal; option 3 depends on issue 039. If those are reworked, the
instructions written here have to be rewritten too, so deciding 002, 003 and 039 first
would avoid documenting behaviour that is about to change.
