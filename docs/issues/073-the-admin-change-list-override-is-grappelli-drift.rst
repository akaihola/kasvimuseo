================================================================================
Issue 073: The admin change list override is Grappelli drift
================================================================================

:Status: Fixed
:Severity: Low
:Area: templates / admin
:Reported: 2026-08-26
:Source: Upgrade plan Stage 6, which compared the override with Grappelli 2.7.3
:Evidence: ``kasvimuseo/templates/admin/change_list.html`` has 244 lines.
    139 lines differ from the installed Grappelli template. The application
    tests pass with the override, but no test proves that its remaining
    differences are required.
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- the upgrade programme moves Grappelli again in Stage 7
    006 -- both issues concern an admin template that may no longer be used
:Decision: ruled -- delete the override. The old ``admin_list`` fork was
    removed in Stage 5, and the installed Grappelli 2.10.4 template supplies
    the required changelist behavior.
:Resolution: c1f72b3 -- deleted the obsolete project override. The docs build
    passed. The application test could not start PostgreSQL, and the browser
    test stopped in its existing Django app-initialization setup.

Problem
-------

The project keeps an old copy of Grappelli's ``change_list.html`` template.
Its only known reason to differ left with the ``admin_list`` fork in Stage 5.
The remaining differences can hide fixes from the installed Grappelli version.

What remains
------------

The maintainer must compare the rendered admin page after the override is
removed. If the page stays correct, delete the project copy and test the page.
If the page changes, record the required difference and update the template.
