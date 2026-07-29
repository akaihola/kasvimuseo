===============================================================
Issue 008: Photologue gallery index raises on an empty database
===============================================================

:Status: Fixed
:Severity: Medium
:Area: urls / third party
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_project_urls.py --
    ``test_photologue_gallery_index_renders_on_an_empty_database`` and
    ``test_photologue_gallery_index_lists_a_gallery`` now pin the fixed
    behaviour; ``test_photologue_urls_are_wired`` proved the include another way
:Depends on: (none)
:Blocks: (none)
:Related: 018 -- a CI job starting from a fresh database is what would catch this
:Decision: Option 2 -- override the route with ``allow_empty=True``
:Resolution: Fixed in c6fc4e3.

Problem
=======

``GET /photologue/gallery/`` raises rather than rendering when there are no galleries:
it is a date-based archive view with ``allow_empty`` off. A fresh database created by
``dev/kasvimuseo db bootstrap`` has no galleries, so the page fails for any new
developer, and for the site until the first gallery exists.

What it raises is ``Http404``, from ``BaseDateListView.get_dated_items``, so the
page answers **404** rather than the 500 first reported here -- Django turns the
exception into the project's 404 page. Measured by running the empty-database
test against the unfixed URLconf. The effect is the same either way: the
dashboard's "The public Photologue galleries" link, and the site's gallery
index, are dead until somebody adds a gallery.

Impact
======

A 404 on a URL reachable from the admin, on any database with no galleries.

Options
=======

1. Create a gallery as part of the bootstrap fixtures.
2. Override the photologue URL with ``allow_empty=True``.
3. Leave it, and note in the README that the gallery index needs at least one gallery.

Decision
========

Option 2. It fixes the site as well as the developer database: option 1 only
papers over the local case and leaves production dead whenever the last gallery
is deleted, and option 3 leaves a link in the admin that does not work.

The installed photologue is 2.6.1 (``requirements/production.txt``), whose
``photologue/urls.py`` routes ``^gallery/$`` to ``GalleryArchiveIndexView``
under the name ``pl-gallery-archive``. ``ylaneenkasvit/urls.py`` now declares
that same path with that same name, calling the same view class with
``allow_empty=True``, ahead of ``include('photologue.urls')`` so it wins the
match. Nothing else in the include is touched and ``reverse('pl-gallery-archive')``
still returns ``/photologue/gallery/``, so the dashboard link and photologue's
own root redirect are unchanged. photologue is not upgraded and no pin moves --
that is 028's work.

Resolution
==========

``ylaneenkasvit/urls.py`` declares the override, and
``kasvimuseo/tests/test_project_urls.py`` gains two tests next to
``test_photologue_urls_are_wired``: the empty database now renders 200 with an
empty ``latest``, and a database with a gallery still lists it. Commit c6fc4e3.
