---
name: docs-build-lock-exits-zero
description: "A concurrent `dev/kasvimuseo docs` prints \"a build is already running\" and exits 0 without building"
metadata: 
  node_type: memory
  type: project
  originSessionId: 937bfb98-ee2c-4eae-9e7d-97e9357f22cd
  modified: 2026-08-01T15:58:29.811Z
---

`dev/docs-build` takes an `flock`; a second invocation while one is running
prints `docs: a build is already running, marked for rebuild` and **exits 0**
without building anything. So "docs build passed" can be a lie if another docs
run (or an earlier backgrounded one) still holds the lock.

**Why:** the warnings-as-errors docs build is one of the three acceptance
commands, and a skipped build is indistinguishable from a clean one by exit
code alone.

**How to apply:** capture the output, not just the status, and require the
final `docs: .../index.html` line before calling it green. Related:
[[run-the-suite-in-the-container]], [[resolution-hash-dies-in-the-rebase]].
