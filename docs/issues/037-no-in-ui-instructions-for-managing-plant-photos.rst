==================================================================
Issue 037: No in-UI instructions for managing plant photos
==================================================================

:Status: Fixed
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
:Decision: Options 1 and 3 as asked, and option 2 in its small form: ``photo``
    is in ``SpeciesAdmin.fieldsets``, with a ``SpeciesForm`` that limits the
    choices to this species' own photos and lets blank detach. 042 made the
    photo *replaceable* -- save the one you want last -- but left it
    impossible to take a photo off a species except by deleting the ``Photo``
    row, which deletes the file for every other use of it, so the capability
    the help text points at was still half missing. Option 4 was left out: with
    1 and 3 in place there is nothing left for a separate page to say that is
    not already on the page where the work happens, and a fourth place to keep
    in step with the code is a fourth place to let drift. Option 3 also needed
    three lines of behaviour: choosing a photo did not enable the Save button,
    so the choice could not be saved at all unless a print tick was toggled
    too, and the honest line above the sheet would have had to say so.
:Resolution: Fixed in badcb5f.

Problem
=======

Nothing in the running application tells the user how plant photos are managed. The
rules exist only in the source code, and a maintainer has to read three files to
reconstruct them:

* ``kasvimuseo/forms.py`` -- ``PhotoForm.clean()`` makes ``title`` optional and derives
  it from the uploaded **filename** with the ``jpg``/``jpeg``/``jpe`` extension removed.
* ``kasvimuseo/models.py`` -- ``autoconnect_photo_to_species`` takes the **first word**
  of that title, lowercases it (``photo_matching.match_key``), and attaches the photo to
  the ``Species`` whose ``name_fi`` matches it case-insensitively. Since 042 it does that
  whether or not the species already has a photo, so the photo saved *last* wins; since
  002 two species sharing a ``name_fi`` go to ``photo_matching.disambiguate``, which
  either narrows them to one or leaves the photo unattached.
* ``kasvimuseo/photos.py`` and the Vue editor in
  ``kasvimuseo/templates/kasvimuseo/reports/planting-labels.html`` -- all photos whose
  title starts with the same word are offered as alternatives on a label, chosen with
  two unlabelled chevron buttons (``&#x2329;`` / ``&#x232a;``) that appear only when
  there is more than one candidate.

So the single most important rule -- *name the file after the Finnish species name, or
the photo attaches to nothing* -- is never stated to the person doing the uploading. The
Photologue upload form shows a ``Title`` field with no hint that leaving it blank is the
normal path, and no hint that its first word is the species key.

The other three operations are undocumented to different degrees, and one of them was
also still missing:

Replacing a photo
    Works, and nothing says so. 042 dropped the ``photo__isnull=True`` filter, so
    uploading a better photo under the same name replaces the old one, and re-saving
    a photo in the admin -- correcting its title, say -- pulls the species photo back
    to it. The workflow this implies, "save the one you want last", is not written
    anywhere the user can see.

Removing a photo
    Not possible. ``Species.photo`` is absent from ``SpeciesAdmin.fieldsets``
    (``kasvimuseo/admin.py``), so a species' photo cannot be detached from the species
    page, and the auto-attach receiver never sets it to ``NULL``. The read-only
    ``photo_image`` column shows a filename the user cannot change. The only route is
    deleting the ``Photo`` object itself, which also deletes the image file for every
    other use of it.

Choosing the photo
    The chevrons in the label editor write ``Label.photo``, and since 039 the read path
    reads it back, so the choice is real and belongs to *that label* rather than to the
    species. Two things are missing rather than wrong: the buttons are glyphs with no
    accessible name, so nothing says which is which or what they change, and choosing a
    photo did not enable the ``Save changes`` button -- only the print tick did -- so the
    choice was lost on the next load unless the user happened to change something else
    as well. Nothing in the interface distinguished "the photo for this species" from
    "the photo on this label".

Impact
======

A user who is not the author cannot upload, remove, replace or re-select a plant photo
without reading the source. Photos that fail to attach fail silently, and the photo
chooser looks like it works while the choice it makes cannot be saved on its own, so the
reports print the wrong plant picture with no indication that anything went wrong.

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
   currently glyphs with no accessible name.
4. **One place to link to.** A short "Kasvikuvat" page in the admin, linked from both the
   photo list and the label editor, describing upload, remove, replace and select in four
   paragraphs -- worth it only if 1--3 are not enough on their own.

Option 1 is text-only and independent of everything else on this list. Option 2 is a
behaviour change and interacts with issues 002 and 003, which are about the same
auto-attach signal; option 3 depends on issue 039. All four of those are ``Fixed``, which
is what let this one be written.

Decision
========

**1, 2 and 3; not 4.** The strings are written in English, wrapped in
``ugettext_lazy`` and ``{% trans %}``, and translated into Finnish in
``locale/fi``; Finnish is what reaches the screen, since ``LANGUAGE_CODE`` is
``fi`` and no ``LocaleMiddleware`` can override it. They name the plant's
Finnish name in words rather than as ``SuomalainenNimi``: that identifier is
the ``verbose_name`` of ``Species.name_fi`` and appears only as one field label
on the species page, so it is not something to send a user looking for. File
names are marked up with ``<code>``, which the admin renders because both
grappelli's and Django's fieldset templates pass ``help_text`` through
``|safe``. Each sentence answers to something in the code:

* ``PhotoForm.image`` and ``PhotoForm.title`` carry the naming rule, what a blank title
  does, and what happens when no species matches -- ``forms.IMAGE_HELP_TEXT`` and
  ``forms.TITLE_HELP_TEXT``.
* The add-photo page carries three sentences above the form: the naming rule, that the
  last save wins and where else the photo can be changed, and what happens to a photo
  whose name is shared by two species. They live in
  ``kasvimuseo/templates/admin/photologue/photo/change_form.html``, which overrides
  grappelli's ``form_top`` block for Photologue photos alone.
* The species page carries the field itself, labelled ``Photo`` / ``Kuva``, with the one thing a
  choice made there cannot promise: saving that photo again in the photo library
  re-attaches it and undoes the choice.
* The label editor names its chevrons and says, above the sheet, that they choose the
  photo *for this label* and that the choice keeps once saved.

Option 2 was checked rather than assumed. 042 made the photo replaceable, so the half
of it about replacing was already true without any admin change; what was still missing
was detaching, which had no route at all short of deleting the image file. That is a
``fieldsets`` line plus a small ``SpeciesForm`` -- the choices are limited to the photos
whose title names this species, through ``photos.get_candidate_photo_pks``, which uses
the same ``match_key`` as the receiver so the two cannot disagree, and the photo the
species already has stays on the list even if its title no longer names the species.
Not a redesign: the receiver is still the only automatic writer, and the help text says
so rather than pretending the field is the last word.

Option 3 turned out to need three lines of JavaScript before its sentence could be
written. Driving the editor in a browser showed the ``Save changes`` button stays
disabled after a photo is chosen: only ``species.visible`` was watched, so the sole way
to save a photo choice was to toggle a print tick as well. Watching ``species.photo_pk``
too is what makes "the choice is kept once you save" a true sentence rather than a
misleading one.

Option 4 is left out. A "Kasvikuvat" page would repeat what the add-photo page, the
species page and the label editor now each say in the place where the user is standing
when the question comes up, and a fourth copy is a fourth thing to keep in step with the
receiver. ``docs/user-guide.rst`` gained the same material in one place for the reader
who wants it as a whole, which is the part of option 4 that was worth having.

The translations are in ``kasvimuseo/locale/fi/LC_MESSAGES/django.po``. The dev container
has no ``gettext``, so the entries were written by hand against the exact source strings
and ``django.mo`` was recompiled with ``polib``; the whole suite asserts the *Finnish*
text on the rendered pages, so a msgid that did not match its source would fail rather
than silently fall back to English.
