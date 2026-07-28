=================================================================
Issue 044: Save buttons reported missing on the species form
=================================================================

:Status: Open
:Severity: High
:Area: admin / grappelli
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: not reproduced -- see below for what was checked
:Depends on: (none)
:Blocks: (none)
:Related: 045 -- the report may turn out to be Grappelli on a tablet
    040 -- the same three buttons, one Finnish and two English
    013 -- another admin declaration that claims something untrue
:Decision: undecided
:Resolution: (none yet)

Problem
=======

As reported: on ``/admin/kasvimuseo/species/<pk>/`` the ``Save and continue
editing``, ``Save and add another`` and ``Tallenna`` buttons are missing, and
the change that caused it is probably from July 2026.

If that is the whole submit row, the species data cannot be edited at all,
which is why this is filed as High.

What was checked
================

**The server still renders all three.** Requesting the page through the test
client at ``398e7ab`` returns them in Grappelli's fixed footer::

    <footer class="grp-module grp-submit-row grp-fixed-footer">
      <li><a href="delete/" class="grp-button grp-delete-link">Delete</a></li>
      <li><input type="submit" value="Tallenna" name="_save" /></li>
      <li><input type="submit" value="Save and add another" name="_addanother" /></li>
      <li><input type="submit" value="Save and continue editing" name="_continue" /></li>
    </footer>

**A browser still shows them.** Chromium against ``dev/kasvimuseo app run`` on
an empty database, at 1440x900, 1180x820 (iPad landscape) and 820x1180 (iPad
portrait): the footer computes to ``position: fixed``, ``visibility: visible``,
``opacity: 1``, ``z-index: 900``, and ``elementFromPoint`` over the ``Tallenna``
button returns that button, so nothing is covering it.

**Nothing in July 2026 touched the page.** ``kasvimuseo/static/css/
kasvimuseo.admin.css`` was last changed in 2011, ``kasvimuseo/admin.py`` at
``c10a156``, and the grappelli and photologue pins have not moved. Every other
July commit is documentation, tests, or the dashboard front page.

So the cause is not in the markup this repository generates, and a plain
``git bisect`` over July has nothing to find. Two candidates remain.

Candidate 1: the buttons never were at the top
----------------------------------------------

``SpeciesAdmin`` sets ``save_on_top = True`` (``kasvimuseo/admin.py``, line 65),
which in stock Django puts a second submit row directly under the page heading.
Grappelli ignores it: its ``templates/admin/change_form.html`` renders
``{% submit_row %}`` once, in ``{% block submit_buttons_bottom %}``, and has no
top block at all. The species form is the longest one in the admin -- eighteen
fields plus the observation inline -- so it is exactly the form where somebody
would reach for the top row, look at the heading, and find nothing.

This is a real defect regardless of what caused the report: an admin option is
set and silently does nothing.

Candidate 2: where the admin CSS comes from
-------------------------------------------

``889edd6`` (28 July 2026) changed that. Before it, a fresh clone had no
``ylaneenkasvit/local_settings.py``, so ``STATIC_URL`` fell back to production's
static host and the admin loaded Grappelli's CSS from
``static.kasvit.ambitone.com``. After it, ``dev/kasvimuseo`` seeds
``local_settings.py`` and the CSS comes from the grappelli installed in the dev
image. If production's static tree carries a different Grappelli build -- one
whose footer is not ``position: fixed``, or which is missing the
``grp-fixed-footer`` rules -- the footer's appearance changes on that commit
without a line of this repository's own code changing. This only affects a dev
checkout; production serves its own static files either way.

Grappelli's own stylesheet has one rule that hides the row from view, and it is
not reached by an iPad::

    @media only screen and (max-device-width: 600px) and (max-device-height: 600px) {
        html .grp-fixed-footer { position: static; ... }
    }

Both dimensions must be at most 600 device pixels, so it applies to phones. It
was confirmed at a 600x600 viewport: the footer stops being fixed and moves to
the end of the document, 1440px down a 600px-tall window -- present, but only
after scrolling past the whole form.

Needed to go further
====================

* The browser and device: a desktop browser, or the iPad of issue 045?
* Is the whole dark footer bar gone, or is the bar there without its buttons?
* Does it happen on other change forms -- ``planting``, ``observation`` -- or
  only on ``species``?
* When was it last seen working, and against which checkout? If it was a clone
  without ``local_settings.py``, candidate 2 is the answer.

Whatever the answer, ``save_on_top = True`` should either be honoured with a
Grappelli template override or removed, so the setting stops claiming something
that is not true.

See also
========

Issue 045 (nothing checks the admin on an iPad), issue 013 (stale ``FIXME``
comments claiming admin features are broken -- the same admin class), issue 040
(half the admin chrome is English -- which is why one button says ``Tallenna``
and the two beside it do not: ``kasvimuseo/locale/fi/LC_MESSAGES/django.po``
translates ``Save`` and neither of the longer labels).
