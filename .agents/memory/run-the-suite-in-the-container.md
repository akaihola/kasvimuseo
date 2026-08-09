---
name: run-the-suite-in-the-container
description: "kasvimuseo's suite runs as dev/kasvimuseo app test, not uv run pytest; podman needs dangerouslyDisableSandbox"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9b957a11-7d9f-4fac-96f7-5f11e15f1746
  modified: 2026-07-29T20:35:29.723Z
---

In `kasvimuseo` the whole stack is Python 2.7 and lives only inside the
container image, so `uv run pytest` fails with `No module named 'pytest'` no
matter what `pytest.ini` says. Run `dev/kasvimuseo app test [args]`, which
starts and stops the throwaway PostgreSQL cluster around the run. Same for
`dev/kasvimuseo docs` (host-side Sphinx, validates the issue register) and
`dev/kasvimuseo app build`.

Every `podman` call in this environment needs `dangerouslyDisableSandbox: true`
— otherwise it dies at `set sticky bit on: chmod /run/user/1002/libpod:
read-only file system` before doing anything.

**Why:** task prompts sometimes quote `uv run pytest` from `pytest.ini`; taking
that at face value costs a round trip and can read as "the suite is broken".

**How to apply:** reach for `dev/kasvimuseo` first; see
[[kasvimuseo-integration-branch-is-master]] for the branch side.
