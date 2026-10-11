---
depends-on: [2, 3, 5, 6, 7, 10]
---

# 08. Refresh public documentation after the repository split

This proposal helps contributors find accurate runtime instructions and public project records after the repository split.

- Priority: Medium.
- Proposed owner: Documentation maintainer.

## Proposed work

1. Update runtime descriptions to match the checked-out code and dependency locks.
2. Remove promises of instructions that the public repository no longer provides.
3. Remove or replace deployment-only issue stubs while preserving valid issue relationships.
4. Remove archive pointers that direct readers to private operational content.
5. Repair commit references and documentation checks after any coordinated history replacement.
6. Rebuild documentation from an empty output directory.

## Review evidence

The prepared [README](../../README.rst) still describes Python 2.7.
[docs/index.rst](../index.rst) promises removed Ansible instructions.
The prepared issue register retains ten deployment-only stubs, and [docs/archive.rst](../archive.rst) points to the earlier operational README.

## Completion checks

- [x] Documentation describes the current runtime and an independent contributor workflow.
- [x] Issue rankings, relationships, and remaining archive references are valid.
- [x] A clean documentation build passes with warnings treated as errors.
- [x] Generated output contains no removed operational pages.

## Dependencies

Use the final content from proposals 02, 03, 05, 06, and 07. Coordinate commit-reference changes with the maintainer.

Update of 2026-10-06: task 10 lands the Django 6.0 runtime that this documentation must describe.
`docs/issues/next.rst`, "Refill this queue before it empties", still sends readers to `AGENTS.md` for the backlog refill rule.
`docs/issues/incoming.rst` still says that `AGENTS.md` states the rule for incoming reports.
`AGENTS.md` no longer holds either rule.
Step 5 waits for private task 4, which replaces public history. If task 4 has not run when this task ends, task 9 repairs the commit references.

## Work done on 2026-10-11

1. `README.rst`, "Testing" and "Continuous integration", `docs/index.rst`, `docs/your-first-change.rst`, `docs/issues/next.rst`, "Facts for a fresh agent", and `docs/api.rst` now describe Django 6.0 on Python 3.12 in the container. The comments in `docs/conf.py`, `dev/docs-build`, `dev/kasvimuseo`, `browser_tests/` and `.github/workflows/tests.yml` say the same.
2. `docs/index.rst` no longer promises Ansible instructions. The private deployment repository owns deployment instructions.
3. `docs/issues/deployment-records.rst` lists the ten reserved numbers 032, 049, 050, 051, 060, 066, 070, 071, 074 and 075. We removed the ten placeholder files and their ranking entries. Issues 025, 026, 031, 036, 057, 059, 065, 067, 068 and 069 no longer name those numbers in `Depends on`, `Blocks` or `Related`. Issue 017 and `README.rst` point at the new page in prose.
4. `docs/archive.rst`, "Removed", holds no entries. The nine removed entries pointed at the pre-split `README.rst`, the emptied `incoming.rst` entries and eight machine-specific memory notes.
5. `docs/issues/next.rst` and `docs/issues/incoming.rst` no longer send readers to `AGENTS.md` for rules that file does not hold. The queue refill rule now names `TASKS.md`.
6. `.agents/memory/private-deployment-records.md` points at the new page instead of the archive.

7. Step 5 ended on 2026-10-11 after private task 4 replaced the public history. Task 9 renamed every commit pointer to the rewritten history; read `docs/tasks/09-integrate-and-publish-public-cleanup.md`, "Work done on 2026-10-11". `docs/archive.rst` now says that a merge does not rewrite a commit, instead of promising that `main` is never rewritten.

## Validation on 2026-10-11

- `dev/kasvimuseo docs --clean` built `.dev/docs/html/index.html` with warnings treated as errors and no warning in `.dev/docs/build.log`.
- `.dev/docs/html/issues/` contains `deployment-records.html` and no `*-deployment-record.html` page.
- Outside the plans and the issue history, the generated pages mention Python 2.7, Django 1.5 or Ansible only in the upgrade plan title.
- `dev/kasvimuseo app test` in the `kasvimuseo-dev-task8` image: 585 passed in 22 seconds.
- `git diff --check` passed.

## Validation of step 5 on 2026-10-11

- `dev/repoint --verbose` on `main` at `261da1c`: 138 pointers, all parked on `refs/clean/`, nothing to re-point. They land when the maintainer publishes the rewritten history.
- `dev/kasvimuseo docs --clean` on the same revision built `.dev/docs/html/index.html` with no warning in `.dev/docs/build.log`.
