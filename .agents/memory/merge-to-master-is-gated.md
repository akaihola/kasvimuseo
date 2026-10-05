---
name: merge-to-master-is-gated
description: "The base-checkout merge is gated until the user asks for it; then it needs the sandbox off, and uncommitted base edits must not collide"
metadata:
  node_type: memory
  type: project
  originSessionId: 8c0aea79-7305-46f6-96a2-08f827b3d076
  modified: 2026-09-26T19:59:55.014Z
---

master is checked out in the base checkout `~/prg/kasvimuseo`, so a
task worktree cannot `git checkout master`; the merge must run as
`git -C ~/prg/kasvimuseo merge --no-ff <branch>`. Two separate
things stand in the way, and they fail differently:

1. **The permission classifier** denies that merge while it is only the
   workflow's own idea (Stage 11, 2026-09-15). When the user explicitly asks
   for it -- the `@mrge` prompt, or "we can merge" -- it goes through
   (2026-09-26).
2. **The sandbox** keeps the base checkout's working tree read-only; only its
   `.git` is writable. The merge then dies with `fatal: read-tree failed`
   after `unable to unlink old '<path>': Read-only file system` (in Finnish:
   `Kirjoitussuojattu tiedostojärjestelmä`). That is sandbox evidence: retry
   with the sandbox off.

**Why:** the classifier guards an outward change the user has not asked for;
the sandbox guards every path outside the task. Neither is a flake.

**How to apply:**

- Without an explicit request, rebase, repair pointers, verify, and stop with
  the branch ready. Name the command the user must run or permit. Do not retry
  variations of it.
- With a request, **check the base checkout for uncommitted edits first**
  (`git -C <base> status --short`). Other sessions leave work there -- on
  2026-09-26 a rewritten memory note and the user's own new incoming report.
  The merge refuses to overwrite a locally modified file, so if the branch
  touches one, stop touching it on the branch (a commit restoring master's
  text), never stash or discard the base edits.
- The `unable to unlink old` error lists the **locally modified** files first,
  even when the merge changes none of them -- it looks like a threat to them
  and is not. Prove it before the sandbox-off retry, without touching any
  working tree:
  `T=$(git -C <base> merge-tree --write-tree master <branch>)`, then
  `comm -12` of `git diff --name-only master $T` against the base's
  `git diff --name-only`. Empty means no collision; `git diff --quiet $T
  <branch>` also shows the merge result equals the tested tip.
- After the merge, confirm the base's pre-existing edits are byte-for-byte as
  before, and report them as left alone rather than calling the checkout
  unclean. Related: [[repoint-repairs-rebased-hashes]].
