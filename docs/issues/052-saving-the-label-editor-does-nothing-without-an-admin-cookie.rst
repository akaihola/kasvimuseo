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
    ``test_the_page_issues_the_csrf_cookie_its_own_save_needs`` and
    ``test_saving_with_no_cookie_says_so_rather_than_nothing``, and adds
    ``test_the_editor_and_its_endpoint_are_staff_only`` and
    ``test_a_save_the_server_refuses_says_so`` for the gate.
:Depends on: (none)
:Blocks: (none)
:Related: 017 -- the browser suite that found this on its first run
    010 -- the same ``post`` handler, which this makes reachable more often
    039 -- the same handler again, and the photo choice a failed save loses
    045 -- the same page, whose remaining half rewrites this template
:Decision: Ruled by the maintainer on 2026-08-01: **option 1 for the fix, and
    the whole of the third question in the same pull request.** The page renders
    the token, and the endpoint stops being public. The evidence that produced
    the second half: ``PlantedSpeciesLabelsApi`` was a bare ``View``
    (``kasvimuseo/views.py``), routed bare (``kasvimuseo/urls.py``) under an
    include with no decorator (``ylaneenkasvit/urls.py:25``), the editor page a
    bare ``TemplateView``; no ``login_required`` and no
    ``staff_member_required`` anywhere on that path, and the only middleware
    touching the POST was ``CsrfViewMiddleware``
    (``ylaneenkasvit/common_settings.py:108``), which is forgery protection and
    not authentication. Measured rather than argued: against
    ``Client(enforce_csrf_checks=True)`` an anonymous request that set its own
    ``csrftoken`` cookie and a matching ``X-CSRFToken`` header was accepted with
    a 200 and left ``Label.objects.count() == 0``. That also settled the first
    half -- rendering the token widened nothing, because a script already had
    what the button lacked.
:Resolution: Fixed in e061b41 (the token) and d03cc21 (the gate).

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

The third question, which outranked both options
================================================

The report asked whether a public URL should be able to rewrite every label at
all, since ``PlantedSpeciesLabelsApi.post`` opens with
``Label.objects.all().delete()`` and rebuilds the table from the request body.
The answer decides whether option 1 is a fix or a widening, and it was the bad
one: **nothing protected the endpoint**. Not the view -- a bare ``View`` -- not
the URL conf, which routed it and the editor page without a decorator, and not
the middleware: ``CsrfViewMiddleware`` is the only one that touches the POST,
and it protects a logged-in user's browser from a third-party page rather than
the endpoint from a stranger. A client that sets its own cookie and matching
header passes it, which is what the measurement in ``Decision`` did.

So option 1 handed a browser no capability that one ``curl`` did not already
have, and the maintainer took both halves: render the token *and* close the
endpoint.

The options
===========

1. **Render the token on the page.** One tag. The middleware then issues the
   cookie for this response, and the existing cookie read finds it, so the
   editor saves for any browser that has the page open. **Taken.**
2. **Leave the token where it is and fail loudly.** Guard the match and say why
   nothing happened. Honest, but on its own the Save button still cannot save.
   **Taken as well, as the fallback** -- rendering the token does not make the
   cookie certain, since a browser can refuse cookies and a sheet can outlive
   one.
3. **Restrict the endpoint.** A different question, and the one that outranked
   the other two. **Taken.** On its own it would have hidden option 1's defect
   rather than fixed it -- a logged-in browser gets the cookie from the login
   form, and an expired cookie under a live session lands back in the same
   silence -- which is why all three are here and not one.

Resolution
==========

Commits e061b41 and d03cc21. All three options, because the ruling
was for all three:

* ``{% csrf_token %}`` is rendered beside the Save button, outside the ``GET``
  form for the box size -- inside it the token would ride along in the query
  string on every "Set box size".
* ``save`` reads the match before indexing it, and an absent cookie now raises
  an ``alert`` naming ``csrftoken`` instead of throwing into the console. The
  ``catch`` around the POST does the same for a rejected save, which used to
  reach ``console.log`` and nowhere else -- so the 403 below is visible too.
* The editor page is wrapped in ``staff_member_required`` and the endpoint in
  ``staff_only_api``, both in ``kasvimuseo/urls.py``. The page answers the way
  the admin does, with a login form at the requested URL; the endpoint answers
  403 with a line of text, because Django 1.5's decorator renders that login
  form behind a **200**, and HTML behind a 200 is exactly what axios cannot
  tell from a saved sheet. ``staff_only_api`` is eleven lines in
  ``kasvimuseo/views.py`` for that reason.
* The gate is on ``is_staff``, not on ``is_superuser``: the museum's own
  accounts are gardeners, and the suite's ``staff_client`` fixture is one of
  those rather than ``admin_client``, so a check written against the wrong
  attribute fails.

What it cost, and it is the cost the ruling accepted: the browser suite now
logs in. ``browser_tests/seed.py`` creates one staff account,
``dev/kasvimuseo`` generates its password per run and passes it to both halves
in ``KASVIMUSEO_BROWSER_TEST_PASSWORD``, and the ``page`` fixture goes through
the admin's login form. No password is written into a tracked file -- that rule
is issue 050, which is what a password in ``conftest.py`` turned out to be
worth. ``docs/user-guide.rst`` gains the sentence that the page is staff-only,
and ``README.rst`` the paragraph about the generated one.

The suite: 419 passing in the container (``dev/kasvimuseo app test``) and 16 in
the browser (``dev/kasvimuseo app browser-test``). Beyond the tests named in
``Evidence``, ``test_labels_api_refuses_anyone_who_is_not_staff`` covers
anonymous and logged-in-but-not-staff on both methods,
``test_the_label_editor_page_shows_a_login_form_to_anyone_else`` covers the
page, and ``test_label_editor_issues_the_csrf_cookie_its_save_reads`` asserts
the server half of the token. One existing assertion moved deliberately:
``test_labels_api_get_reads_the_label_photo_without_more_queries`` counts 16
queries where it counted 14, and the two new ones are the session row and the
user it names -- what every admin page already pays.

See also
========

Issue 017 (the suite that found this), issues 010 and 039 (the same ``post``
handler, now behind the gate), issue 045 (the same page), issue 050 (why no
password is in a tracked file).
