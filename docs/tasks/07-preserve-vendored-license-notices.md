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

- Each copy was compared with its upstream version. The date-picker code and one template differ. Read `docs/third-party-notices.rst`, "What the check on 2026-10-10 found".
- The upstream django-jqm archive has no license file. Its `setup.py` and the Launchpad project page declare MIT, which `jqm/LICENSE` records.
- The full application suite passed in the development image: 570 tests, including the 13 new notice tests and the 10 release artifact tests.
- A negative control removed `jqm/LICENSE`; two notice tests failed and named the file.
- `dev/kasvimuseo docs --clean` built without warnings and rendered `third-party-notices.html`.
- The production image build was not run; it checks the same three files after `pip install`.

## Related work

Coordinate project metadata with [proposal 06](06-declare-project-license.md).

## Review correction, 2026-10-11

The correction resolves R1, R2, and S1 from the independent review.

1. The dashboard template now carries its upstream notices in source distributions, wheels, and the production image.
2. `docs/third-party-notices.rst`, "The inventory", records the copied template and its notice file.
3. The same document, "What the check on 2026-10-10 found", records the date-picker code changes.
4. The notice tests parse every inventory row and check complete notice contents against reviewed hashes.
5. Regression checks reject rows with missing files and a notice reduced to its copyright line.

Task 7 remains unchecked in `TASKS.md` until the user accepts it.

## Validation on 2026-10-11

- The full application suite passed after rebasing on current `main`: 598 tests.
- The browser suite passed: 79 tests and seven touch checks skipped. `browser_tests/conftest.py` explains the skips.
- `dev/kasvimuseo docs --clean` built the documentation without warnings.
- The production image build passed. Its installed dashboard notice matched the reviewed file byte for byte.
- The rerun also found a stale assertion after task 4 changed an ignore rule. Commit `test(settings): drop stale ignore rule assertion` removes it.
