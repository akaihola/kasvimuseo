=======================================================================
Issue 013: Stale FIXME comments claim working admin features are broken
=======================================================================

:Status: Open
:Severity: Low
:Area: admin / documentation
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_admin_changelist.py, kasvimuseo/tests/test_admin_forms.py
:Depends on: (none)
:Blocks: (none)
:Related: 017 -- option 2 here wants the browser test that 017 is about
    044 -- ``save_on_top`` is the same fault as a setting rather than a comment
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``kasvimuseo/admin.py`` carries standing comments that the tests disprove:

* ``# FIXME: action selection doesn't work`` -- the "Create Species Sheets" action works
  when driven through the changelist POST, returning a 302 to ``/planted-species/22,11/``.
* ``# FIXME: filtering doesn't work`` on ``SpeciesAdmin``, ``ObservationAdmin`` and
  ``CareAdmin`` -- every documented ``list_filter`` narrows the rows correctly, and the
  Grappelli filter pulldown renders working links.

Both are now covered by tests, so a real regression would be caught.

Impact
======

Readers avoid or work around features that function, and the comments hide whatever the original problem actually was.

Options
=======

1. Delete the comments.
2. If the original symptom is remembered and is real but different -- for example a
   Grappelli interaction only visible in a browser -- rewrite them to say what actually
   fails, and add a browser test (see issue 017).
