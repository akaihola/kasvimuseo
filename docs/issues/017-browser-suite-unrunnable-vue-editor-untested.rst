================================================================================
Issue 017: Browser test suite is unrunnable, so the Vue label editor is untested
================================================================================

:Status: Open
:Severity: High
:Area: tests / gap
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: integration_tests/ (not part of the default suite)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``reports/planting-labels.html`` is a 626-line Vue application -- the label editor staff
use to group, hide and photograph planting labels. The Django side is covered: the JSON
endpoint, the POST round trip, and the page's server contract (200, the ``#app`` mount
point, the data endpoint URL, the Vue script tag). **None of its actual behaviour is** --
drag and drop, the save cycle and the layout only exist in the browser.

The repository has a browser suite, ``integration_tests/``, but it cannot run:

* it hardcodes ``http://localhost:8000/`` and expects a server to be up already;
* ``conftest.py`` logs in with a real username and password committed to the repo;
* ``conftest.py`` asserts the login page URL is ``/admin/`` *before* logging in, which is
  wrong, so the fixture fails at the first assertion;
* it needs SeleniumBase and a browser, neither of which the dev container has.

Impact
======

The most complex user-facing feature in the project has no behavioural test at all, and the suite that was meant to cover it does not run.

Options
=======

1. Rebuild it on Django's ``LiveServerTestCase``, which starts its own server and needs
   no hardcoded host or committed password, and add a browser to the dev image.
2. Delete ``integration_tests/`` if it is not going to be maintained, so it stops looking
   like coverage that exists.

Related: ``dev/kasvimuseo`` would need an ``app browser-test`` entry point, and the CI
question in issue 018.
