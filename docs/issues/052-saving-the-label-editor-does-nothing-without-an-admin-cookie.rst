=======================================================================
Issue 052: Saving the label editor does nothing without an admin cookie
=======================================================================

:Status: Fixed
:Severity: Medium
:Area: templates / labels UI
:Reported: 2026-07-31
:Source: Issue 017's browser suite, first run, via ``docs/issues/incoming.rst``
:Evidence: ``browser_tests/test_label_editor.py::
    test_saving_without_an_admin_cookie_does_nothing_and_says_nothing`` pinned
    the silence: no cookie, no request, no message. The fix replaces it with
    ``test_saving_works_for_a_browser_that_did_not_come_through_the_admin``
    and ``test_saving_with_no_cookie_says_so_rather_than_nothing``.
:Depends on: (none)
:Blocks: (none)
:Related: 017 -- the browser suite that found this on its first run
    010 -- the same ``post`` handler, which this makes reachable more often
    039 -- the same handler again, and the photo choice a failed save loses
    045 -- the same page, whose remaining half rewrites this template
:Decision: Ruled here on 2026-08-01 on the evidence, because the question did
    not reach the maintainer: ``ask_user_question_kandev`` was put twice and
    neither call came back. **Option 1, with option 2 kept as the fallback.**
    The third question decided the first: the endpoint is not protected by
    anything, so rendering the token widens nothing. ``PlantedSpeciesLabelsApi``
    is a bare ``View`` (``kasvimuseo/views.py:46``), routed bare
    (``kasvimuseo/urls.py:24-26``) under an include with no decorator
    (``ylaneenkasvit/urls.py:25``); the editor page is a bare ``TemplateView``
    (``views.py:42``). There is no ``login_required`` and no
    ``staff_member_required`` anywhere on that path, and the only middleware
    that touches the POST is ``CsrfViewMiddleware``
    (``ylaneenkasvit/common_settings.py:108``), which is forgery protection
    rather than authentication. Measured rather than argued: against
    ``Client(enforce_csrf_checks=True)``, an anonymous request that sets its own
    ``csrftoken`` cookie and a matching ``X-CSRFToken`` header is accepted
    (``200``) and leaves ``Label.objects.count() == 0``. A script can already do
    what the button could not, so the browser gets nothing new. Whether that
    endpoint should be public at all is a separate ruling with its own cost --
    a logged-in browser suite -- and is back in :doc:`incoming` as a report.
:Resolution: Fixed in e061b41.

Problem
=======

``reports/planting-labels.html`` sends the sheet with axios, and takes the CSRF
token out of the cookie::

    const token = document.cookie.match(/\bcsrftoken=(\w+)/)[1];

The page rendered no ``{% csrf_token %}``. Nothing else on it called
``get_token()`` either, so ``CsrfViewMiddleware`` had no reason to put a
``csrftoken`` cookie on the response -- it sets one only for a response whose
rendering asked for the token. For a browser that had never been given the
cookie by some other page, ``match`` returns ``null``, ``null[1]`` throws, and
the throw happens inside the ``v-on:click`` handler: Vue logs it and returns.

So nothing happens. No request leaves the browser, the button does not change,
no message appears, and the only trace is a ``TypeError`` in a console nobody
has open.

Impact
======

Staff reach the editor from the admin dashboard, and the admin login form
renders the token, so the cookie is there and the save works -- which is why
eight years of use never met this. It bites anyone who opens
``/kasvimuseo/planting-labels/`` directly, from a bookmark or a link, and
anyone whose ``csrftoken`` cookie has expired (a year by default) or been
cleared. What they get is a Save button that lies: the drag-and-drop work of
regrouping museum numbers, the per-label photo choices of issue 039 and the
print toggles of 047 are all discarded on the next reload, with nothing on
screen having suggested they were not saved.

The third question, which outranks both options
===============================================

The report asked whether a public URL should be able to rewrite every label at
all, since ``PlantedSpeciesLabelsApi.post`` (``kasvimuseo/views.py:137``) opens
with ``Label.objects.all().delete()`` (line 153) and rebuilds the table from
the request body. The answer decides whether option 1 is a fix or a widening,
and it is stated in ``Decision`` above with its files and lines: **nothing
protects the endpoint today**. Not the view, not the URL conf, not the
middleware.

That means option 1 hands a browser no capability that ``curl`` did not already
have -- the measurement in ``Decision`` is one anonymous request that empties
the table -- so the CSRF fix is safe to make now. It also means the register is
carrying an authorization defect that nobody had written down, which is why it
went back to :doc:`incoming` as its own report rather than being folded in
here: gating the view changes what production allows, wants a ruling of its
own, and costs the browser suite a seeded staff account and a login -- next
door to what issue 050 was about.

The options
===========

1. **Render the token on the page.** One tag. The middleware then issues the
   cookie for this response, and the existing cookie read finds it, so the
   editor saves for any browser that opens the URL. Nothing about who may post
   changes.
2. **Leave the token where it is and fail loudly.** Guard the match and say
   "open this page from the admin" when there is no cookie. Honest, but the
   Save button still cannot save, and the workflow stays "go through the admin
   first" -- which is a rule nothing states and nothing enforces.
3. **Restrict the endpoint instead.** Making the page staff-only would give a
   logged-in browser the cookie as a side effect, so it would hide this defect
   without fixing it -- an expired cookie on a live session still lands in the
   same silence. It is a different question, kept as one.

Options 1 and 2 are not exclusive, and the reason to take both is in the last
sentence of option 3: rendering the token does not make the cookie certain. A
browser refusing cookies for the site, or a page restored from the back-forward
cache after the cookie expired, still arrives at ``save`` with nothing to read.

Resolution
==========

Commit e061b41. Option 1 with option 2 behind it:

* ``{% csrf_token %}`` is rendered beside the Save button, outside the ``GET``
  form for the box size -- inside it the token would ride along in the query
  string on every "Set box size".
* ``save`` reads the match before indexing it, and an absent cookie now raises
  an ``alert`` naming ``csrftoken`` instead of throwing into the console.
* The browser suite's ``editor`` fixture no longer stops at ``/admin/`` on the
  way in. That hop existed only to borrow the admin's cookie, so every test in
  the file now arrives the way a bookmark does.

The suite: 416 passing in the container (``dev/kasvimuseo app test``), 14 in the
browser (``dev/kasvimuseo app browser-test``).
``test_label_editor_issues_the_csrf_cookie_its_save_reads`` in
``kasvimuseo/tests/test_templates.py`` asserts the server half -- the response
carries the cookie and the page carries both the token and the read -- and the
two browser tests named in ``Evidence`` assert the round trip and the message
that is left when the cookie is gone.

See also
========

Issue 017 (the suite that found this), issues 010 and 039 (the same ``post``
handler), issue 045 (the same page), and :doc:`incoming` for the authorization
report this one produced.
