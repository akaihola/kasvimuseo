Issue 080: The label under a landscape photo is too narrow
==========================================================

:Status: In progress
:Claimed: 0b0a8ad8-79f0-4346-85f9-946bc52db68c
:Severity: Medium
:Area: templates / public species
:Reported: 2026-09-27
:Source: Maintainer report in ``docs/issues/incoming.rst``
:Evidence: (none yet) -- the report describes a visible width mismatch on the compact species page.
:Depends on: (none)
:Blocks: (none)
:Related: (none)
:Decision: undecided
:Resolution: (none yet) -- the label under a landscape photo does not match the photo width.

Problem
=======

On the planted species compact view, the label below a landscape photo is too narrow. The label matches portrait photos. Its borders must match the photo borders for both orientations.

Work
----

The photo and label are rendered by ``kasvimuseo/templates/kasvimuseo/reports/planted-species.html``. Their widths are set in ``static/css/planted-species-printable.css``. Fix the width rule and add a focused regression check.
