---
depends-on: [10]
---

# 14. Close the runtime upgrade programme

This task helps maintainers end issue 036 after the last upgrade stage lands.

- Priority: Medium.
- Owner: Project maintainer.

## Work

1. Check that `docs/upgrade-plan.rst` on `main` shows every stage as done.
2. Decide whether issue 036 ends with the source upgrade or with a deployment of the new runtime.
3. Update the status, decision, and resolution of issue 036 to match that choice.

## Evidence

Issue 036 stays `Accepted` until the upgrade programme ends.
Stage 19, Django 6.0.7, is the last stage, and task 10 lands it.
The private deployment repository tracks the host work for the new runtime.

## Completion checks

- [ ] Issue 036 has a status and a decision that match the state of the programme.
- [ ] A clean documentation build passes.

## Work done on 2026-10-11

1. `docs/upgrade-plan.rst` on `main` shows Stages 0 to 19 as `Done`.
2. The programme ends with the source upgrade. The private deployment repository owns the host work, so the public record cannot track a deployment.
3. Issue 036 now reads `Fixed`. Its decision records that choice, and its resolution names the Stage 19 merge and upgrade commits.

## Validation on 2026-10-11

- `dev/kasvimuseo docs --clean` built `.dev/docs/html/index.html` with no warnings. The generated register lists issue 036 as `Fixed`.
- `dev/kasvimuseo app test kasvimuseo/tests/test_issue_register.py kasvimuseo/tests/test_commit_pointers.py` in the `kasvimuseo-dev-task14` image: 78 passed.
