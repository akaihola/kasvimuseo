---
depends-on: []
---

# 07. Preserve vendored dependency license notices

This proposal helps maintainers retain the license notices required for code and assets copied from upstream projects.

- Priority: Medium.
- Proposed owner: Dependency maintainer.

## Proposed work

1. Inventory vendored Python, JavaScript, CSS, templates, and other copied assets.
2. Check the license and notice requirements against the exact upstream versions.
3. Restore missing license texts or notices.
4. Preserve attribution during the personal-information cleanup.
5. Include applicable notices in published artifacts.

## Review evidence

[jqm/README.rst](../../jqm/README.rst) identifies an MIT-licensed upstream project, but the prepared tree has no separate jqm license text.
Review `jqm/`, `browser_tests/vendor/`, and copied assets under `kasvimuseo/static/`.

## Completion checks

- [x] Each vendored component has a recorded origin, version, and applicable license.
- [x] The repository and distributed artifacts retain the required notices.
- [x] Removing personal examples does not remove upstream attribution.

## Work done on 2026-10-10

1. `docs/third-party-notices.rst` lists the six copies with origin, version, license and notice file. `docs/index.rst` links it under "Reference".
2. `jqm/LICENSE` supplies the MIT text that the upstream archive lacks. `jqm/README.rst`, "License", points to it.
3. A `.LICENSE.txt` file beside each copied asset holds the upstream license text: fitty, the jQuery UI date picker, Vue, axios and sanitize.css.
4. `setup.py`, `MANIFEST.in`, `dev/check-release-artifacts` and `Dockerfile` carry and check the three notices that ship in release artifacts.
5. `kasvimuseo/tests/test_third_party_notices.py` ties the inventory to the tree. `kasvimuseo/tests/test_release_artifacts.py` requires the notices in both artifacts.
6. `docs/tasks/03-replace-operational-data-and-personal-examples.md` tells the cleanup to keep the author names inside the notice files.

## Validation on 2026-10-10

- Every copy was compared byte for byte with the upstream file at the recorded version. One template differs on purpose; the notices page records it.
- The upstream django-jqm archive has no license file. Its `setup.py` and the Launchpad project page declare MIT, which `jqm/LICENSE` records.
- The full application suite passed in the development image: 570 tests, including the 13 new notice tests and the 10 release artifact tests.
- A negative control removed `jqm/LICENSE`; two notice tests failed and named the file.
- `dev/kasvimuseo docs --clean` built without warnings and rendered `third-party-notices.html`.
- The production image build was not run; it checks the same three files after `pip install`.

## Related work

Coordinate project metadata with [proposal 06](06-declare-project-license.md).
