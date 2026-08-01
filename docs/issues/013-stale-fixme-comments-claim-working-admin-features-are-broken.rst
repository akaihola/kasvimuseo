=======================================================================
Issue 013: Stale FIXME comments claim working admin features are broken
=======================================================================

:Status: Fixed
:Severity: Low
:Area: admin / documentation
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_admin_changelist.py, kasvimuseo/tests/test_admin_forms.py
:Depends on: (none)
:Blocks: (none)
:Related: 017 -- option 2 here wants the browser test that 017 is about
    044 -- ``save_on_top`` is the same fault as a setting rather than a comment
:Decision: Option 1 -- delete all five comments -- with option 2's browser test
    taken as well, because it is what settles the choice between them rather
    than an extra. 017's suite made that cheap: two tests now drive the filter
    pulldown and the action dropdown in Chromium against a served instance, and
    both features work there exactly as they do under the test client. The
    symptom option 2 guessed at is real but is not a failure: Grappelli's copy
    of ``actions.js`` shadows Django's and deletes the "Go" button, submitting
    the changelist form from the dropdown's ``change`` event instead, so an
    action runs the moment it is chosen and there is no button to press. That
    is what "action selection doesn't work" was looking at.
:Resolution: 243105b -- the five comments deleted from ``kasvimuseo/admin.py``,
    ``browser_tests/test_admin_changelist.py`` added with the two checks that
    settled the choice, and ``browser_tests/seed.py`` given the permissions and
    the second ``type`` those checks need.

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

What the browser showed
=======================

Both options turn on the same question -- is there a Grappelli interaction the
test client cannot see? -- so it was asked rather than argued about.
``browser_tests/test_admin_changelist.py`` drives the species changelist in
Chromium, and the two JavaScript controls a test client never touches both
work:

* **The filter.** The sidebar is a pulldown that starts hidden and a
  ``<select class="grp-filter-choice">``; ``grappelli.initFilter`` opens the
  one on click and sets ``location.href`` from the other on ``change``.
  Choosing *Yrtti* narrows three species to the one.
* **The action.** Ticking a row and choosing "Create Species Sheets" lands on
  ``/kasvimuseo/planted-species-printable/2/`` -- the same redirect
  ``test_admin_forms.py`` gets from the POST -- with no console errors.

The action is where the original comment came from. Grappelli 2.4.5 ships its
own ``admin/js/actions.js``, which shadows Django's through the app template
and static loaders, and it ends::

    // GRAPPELLI CUSTOM: submit on select
    $(options.actionSelect).attr("autocomplete", "off").change(function(evt){
        $(this).parents("form").submit();
    });

Django's "Go" button is gone with it: the rendered changelist has no submit
control at all, which the browser test asserts. So an action runs as soon as
it is picked from the dropdown, and a reader looking for a button to press
finds none. That is a surprise, not a defect, and it is Grappelli's to own --
this repository neither configures nor patches it. The comments went, and the
browser test is what keeps the answer.

The one thing the check needed was data: ``browser_tests/seed.py`` gave every
species the factory's default ``type``, so the ``type`` filter had nothing to
narrow, and its gardener account was staff with no model permissions, so the
changelist answered 403. Both are fixed there, in the seed rather than in a
fixture, since the browser suite has one database for all of its tests.
