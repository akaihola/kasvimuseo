---
depends-on: []
---

# 13. Finish the iPad label checks

This task helps the person with the garden's iPad confirm label behaviour that no emulator can show.

- Priority: Medium.
- Owner: The maintainer, or another person with the iPad.

## Work

1. Do items 2, 3, and 4 in `docs/issues/056-ipad-label-text-is-doubled-and-grows-until-it-vanishes.rst`, "What is left".
2. Record each result in issue 056.
3. Set the status of issue 056 from the results.
4. Remove the `:Claimed:` field of issue 056.

## Evidence

Issue 056 is `In progress`.
Its `:Claimed:` field names `feature/fix-ipad-label-text-4ic`, and no branch has that name.
The branch `feature/fix-ipad-label-text-056` holds only a claim commit.
The maintainer did items 1 and 5 on the iPad on 2026-08-02.

## Completion checks

- [x] Issue 056 records the results of items 2, 3, and 4.
- [x] Issue 056 has a status that matches the results and no `:Claimed:` field.

## Work done on 2026-10-12

Production does not carry the fix, so the agent served the integration commit from a development server on the tailnet.
The maintainer opened the label editor on the iPad through the development login and did items 2, 3, and 4.
The maintainer reported that the text stays stable, that the printed sheet uses the printed size, and that the text size is good.
The agent recorded the three results in issue 056 under "What the device said", "The second look, 2026-10-12".
The agent set the status of issue 056 to `Fixed`, named 312bf15 in `:Resolution:`, and removed the `:Claimed:` field.
The agent stopped the development server after the look.

## Validation on 2026-10-12

- `dev/kasvimuseo app test kasvimuseo/tests/test_issue_register.py` in the `kasvimuseo-dev-task13` image: 42 passed.
- `dev/kasvimuseo docs --clean` built `.dev/docs/html/index.html` with no warning in `.dev/docs/build.log`.
- `dev/repoint --verbose`: 138 pointers, all parked, nothing to re-point.
- `git diff --check` passed.
