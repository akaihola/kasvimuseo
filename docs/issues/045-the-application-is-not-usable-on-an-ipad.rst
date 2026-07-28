=========================================================
Issue 045: The application is not usable on an iPad
=========================================================

:Status: Open
:Severity: Medium
:Area: templates / mobile
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: (none -- no test runs any page in a mobile browser; see issue 017)
:Depends on: (none)
:Blocks: (none)
:Related: 017 -- nothing runs any page in a browser, let alone a tablet one
    044 -- may be this issue seen from the species form
    046, 047 -- the label editor's two controls, on a screen with no pointer
    006 -- ``mobile-base.html``, the abandoned start of a mobile front end
:Decision: undecided
:Resolution: (none yet)

Problem
=======

Reported as one line -- "ensure everything works on an iPad" -- with no detail,
so **what "everything" covers still needs saying**: the admin, the label
editor, the printable species sheets, the public list, or all of them. What
follows is what a reading of the templates says an iPad will hit, so the
question can be answered against something concrete.

The tablet is the natural device for this application: the users are gardeners,
the data is entered where the plants are, and every page is either the admin or
a report rendered from it.

Not one page declares a viewport
--------------------------------

No template in the repository contains ``<meta name="viewport">``. iOS Safari
therefore lays every page out at its 980px fallback width and scales the result
down to the screen, so text is small, tap targets are smaller, and the first
gesture on every page is a pinch. This is one line per base template and is the
single cheapest thing on this list.

Grappelli does not adapt to a tablet
------------------------------------

Grappelli 2.4's only responsive rule is::

    @media only screen and (max-device-width: 600px) and (max-device-height: 600px)

Both dimensions must be at most 600 device pixels, so an iPad gets the full
desktop layout: the fixed footer, the fixed header, and the sidebar filters.
See issue 044, where the missing save buttons may turn out to be exactly this.

The label editor cannot work on a touch screen
----------------------------------------------

``reports/planting-labels.html`` moves museum numbers between labels with the
HTML5 drag-and-drop API -- ``dragstart``, ``dragenter``, ``dragover``, ``drop``
-- which iOS Safari does not generate from touch. The editor's core interaction
is unreachable on an iPad; only the photo arrows and the save button respond.

Its second control is hover-only. The print toggle is hidden until the pointer
is over the label::

    .remove { opacity: 0; }
    li:hover .remove { opacity: 0.5; }

There is no hover on a touch screen, so the control the user guide tells staff
to use -- "poista tulostusrasti kyltin oikeassa alalaidassa" -- is invisible
there. Issue 047 covers the same control's glyph.

Nothing would notice a regression
---------------------------------

The suite is entirely server-side, and the browser suite cannot run at all
(issue 017), so every claim above comes from reading the templates and none of
it is pinned by a test. Whatever is decided here, "works on an iPad" cannot be
kept true without something that checks it -- Playwright's WebKit at an iPad
viewport is the cheap version, a real device the honest one.

Impact
======

Unknown until the scope is settled, which is the point of filing this. If the
answer is "the admin, for entering observations in the garden", the work is the
viewport tag plus whatever issue 044 turns out to be. If it includes the label
editor, it is a rewrite of its drag-and-drop layer with pointer events, and
issues 046 and 047 belong to the same piece of work.

See also
========

Issue 017 (the browser suite is unrunnable, so the Vue editor is untested),
issue 044 (save buttons on the species form), issue 046 (the label editor opens
at print size), issue 047 (the print toggle's glyph), issue 006 (which now also
covers ``mobile-base.html``, the abandoned start of a mobile front end).
