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

- [ ] Each vendored component has a recorded origin, version, and applicable license.
- [ ] The repository and distributed artifacts retain the required notices.
- [ ] Removing personal examples does not remove upstream attribution.

## Related work

Coordinate project metadata with [proposal 06](06-declare-project-license.md).
