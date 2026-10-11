---
depends-on: [10]
---

# 03. Replace operational data and personal examples

This proposal helps maintainers explain application behavior with synthetic examples and remove unnecessary personal information.

- Priority: Medium.
- Proposed owner: Application and documentation maintainers.

## Proposed work

1. Review retained issues for extracts, identifiers, counts, and observations from real installation data.
2. Preserve the original evidence privately.
3. Replace those details with synthetic examples that demonstrate the same application behavior.
4. Replace personal names and account names in fixtures and usage examples.
5. Preserve author credits, copyright notices, and upstream attribution.

## Review evidence

The review found installation-specific evidence in issues 002, 011, 041, 053, 054, and 056.

Examples include [issue 041](../issues/041-duplicate-observation-numbers-crash-the-observation-page.rst) and [issue 054](../issues/054-the-species-list-names-a-photo-size-the-fixtures-lack.rst).
[The admin fixture](../../kasvimuseo/tests/test_admin.py) and [development-login example](../../ylaneenkasvit/dev_login.py) also use personal identities.

## Completion checks

- [x] Public explanations retain the bug trigger, expected behavior, and decision without exposing installation data.
- [x] Changed fixtures still exercise the same behavior in the affected tests.
- [x] A scan of tracked text and translation catalogs finds no unnecessary personal or operational details.

## Related work

Coordinate attribution changes with [proposal 07](07-preserve-vendored-license-notices.md).
Task 7 lists the notice files in `docs/third-party-notices.rst`; keep the author names and addresses inside them.

Update of 2026-10-06: task 10 adds issues 087, 088, and 089. Issue 089 records an observation from the production dump of 2026-08-26.
Include those issues in step 1.

## Work done on 2026-10-11

1. The private deployment repository keeps the original evidence in `docs/public-issue-evidence.rst`, with the public commit that holds the original text.
2. Issues 002, 006, 011, 020, 041, 042, 045, 053, 054, 055, 056, 063 and 089 now describe the installation without counts, identifiers, file names, device versions or machine paths.
3. `kasvimuseo/tests/test_signals.py` uses two synthetic `tarhapioni` namesakes and synthetic house names for the same disambiguation test.
4. `kasvimuseo/tests/test_admin.py` creates a synthetic contact. `ylaneenkasvit/dev_login.py` shows the `puutarhuri` account in its example URL.
5. `docs/user-guide.rst`, "Projektin muistilista", names the maintainer by role.
6. Author credits stay: `LICENSE`, `docs/conf.py`, the translation catalog headers, the upstream fork URLs and `docs/third-party-notices.rst`.
7. `.agents/memory/synthetic-examples-in-public-records.md` records the convention.

Issues 087 and 088 record only local validation results and needed no change.

## Validation on 2026-10-11

- `dev/kasvimuseo app test` in the `kasvimuseo-dev-task3` image: 576 passed, 6 skipped.
- `dev/kasvimuseo docs --clean` built `.dev/docs/html/index.html` with warnings treated as errors.
- A scan of tracked text and the two translation catalogs for personal names, place names, device versions and dump references found only author credits and upstream attribution.
