---
name: merge-to-master-is-gated
description: "master is checked out in the base checkout; the auto-mode classifier denies `git -C ~/prg/kasvimuseo merge` from a task worktree"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8c0aea79-7305-46f6-96a2-08f827b3d076
  modified: 2026-08-24T20:25:26.470Z
---

A kandev task worktree cannot finish the `merge --no-ff` step of the
integration flow ([[repoint-repairs-rebased-hashes]]). `git checkout master`
fails in the worktree ("already used by worktree at /home/agent/prg/kasvimuseo"),
and running the merge via `git -C /home/agent/prg/kasvimuseo` is denied by the
permission classifier.

**Why:** the merge mutates the base checkout, which sits outside the task
sandbox; the denial is intentional, not a flake.

**How to apply:** rebase, repair pointers, verify, and stop with the branch
ready. Say in the report that the merge into local master is the step the user
must run or permit: `git -C /home/agent/prg/kasvimuseo merge --no-ff <branch>`.
Do not retry variations of the merge.
