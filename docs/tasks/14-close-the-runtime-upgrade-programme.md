---
depends-on: [10]
---

# 14. Close the runtime upgrade programme

This task helps maintainers end issue 036 after the last upgrade stage lands.

- Priority: Medium.
- Owner: Project maintainer.

## Work

1. Check that `docs/upgrade-plan.rst` on `master` shows every stage as done.
2. Decide whether issue 036 ends with the source upgrade or with a deployment of the new runtime.
3. Update the status, decision, and resolution of issue 036 to match that choice.

## Evidence

Issue 036 stays `Accepted` until the upgrade programme ends.
Stage 19, Django 6.0.7, is the last stage, and task 10 lands it.
The private deployment repository tracks the host work for the new runtime.

## Completion checks

- [ ] Issue 036 has a status and a decision that match the state of the programme.
- [ ] A clean documentation build passes.
