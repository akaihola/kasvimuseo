---
name: kasvimuseo-integration-branch-is-master
description: "In kasvimuseo, branch from and rebase onto master; dev-environment is an already-merged historical branch"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5d5084eb-a27f-4ce9-8df8-04bed002934f
  modified: 2026-07-31T22:53:14.200Z
---

In `kasvimuseo`, the integration branch is `master`. Harness/session context may
report the main branch as `dev-environment` — it is wrong. As of 2026-07-29 no
local `dev-environment` branch exists; only `origin/dev-environment` (adf4ca9),
which is already an ancestor of local `master`. Local `master` is also well ahead
of `origin/master`.

**Why:** taking the harness at its word would target a PR at a stale,
already-merged branch, or fail outright since the ref is not local.

**How to apply:** branch from and rebase onto **local** `master`, per
[[use-worktrees-never-switch-base]]. Verify with
`git merge-base --is-ancestor origin/dev-environment master` before believing any
future claim to the contrary.

Rebase onto local `master`, not `origin/master`: local master carries merges of
finished sibling task branches that have not been pushed, so a task branch is
normally based on commits `git log origin/master..HEAD` will list as if they were
yours. Check the parent (`git log --graph`) before "cleaning up" a branch that
looks like it duplicates another task's commits — rebasing onto `origin/master`
would drop work that is only on local master.
