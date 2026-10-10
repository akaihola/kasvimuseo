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

- [ ] Public explanations retain the bug trigger, expected behavior, and decision without exposing installation data.
- [ ] Changed fixtures still exercise the same behavior in the affected tests.
- [ ] A scan of tracked text and translation catalogs finds no unnecessary personal or operational details.

## Related work

Coordinate attribution changes with [proposal 07](07-preserve-vendored-license-notices.md).
Task 7 lists the notice files in `docs/third-party-notices.rst`; keep the author names and addresses inside them.

Update of 2026-10-06: task 10 adds issues 087, 088, and 089. Issue 089 records an observation from the production dump of 2026-08-26.
Include those issues in step 1.
