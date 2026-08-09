---
name: resolution-hash-dies-in-the-rebase
description: "An issue file's :Resolution: hash is unreachable after the branch is rebased -- re-point it as the last step before handing over"
metadata: 
  node_type: memory
  type: project
  originSessionId: 053abdfd-44d5-4005-81ea-3400ab5361cd
  modified: 2026-08-08T17:52:23.028Z
---

Every kasvimuseo fix writes its own commit hash into the issue file's
`:Resolution:` field, in the same branch as the fix. Every branch is then
**rebased** onto `master` before it is merged — see
[[kasvimuseo-integration-branch-is-master]]. The rebase rewrites the fix commit,
so the hash the issue file names stops existing: `git show` on it fails and the
register points at nothing.

Since master's `0ecc30d`, `dev/kasvimuseo docs` does check the hashes — and
as of 2026-08-08 it checks **reachability** (branch or tag), not just object
existence: the Stage 5 docs build failed on Stage 4's dead `b8eb855` with "no
branch and no tag reaches it", and `dev/repoint --write` repaired it (to
`fa8ac5f`, by patch identity). So a dead pointer inherited from an earlier
branch now breaks *your* docs build; run `dev/repoint` rather than mapping by
hand.

It happened on 020/021/033 (2026-07-31, merged naming `54cc2fa`, corrected to
`0c82b49` afterwards).

Recovering a dead pointer works: `git patch-id --stable` over `git rev-list
master` mapped 16 of 18 dead pointers uniquely, and commit-subject match over
master got a 17th. The 18th (`55ce0a8` in issue 062) is *deliberately* off
master, parked on tag `interim-062-option-2` — a pointer reachable from a tag is
intentional and must not be "corrected".

**How to apply:** after any rebase, and again immediately before reporting the
work finished, re-read the hash out of `git log` and rewrite it in every issue
file the branch touches:

    git log --oneline -3                       # the fix commit's *current* hash
    grep -rn "^:Resolution:" docs/issues/       # what the files still claim
    git cat-file -t <hash>                     # fails loudly if it is stale

Two related things that also go stale in the same window, both worth re-running
rather than re-reading: a **test count** quoted in an issue file (`405 passed`
became 406 when another branch's regression test landed), and a plain
`grep -rn ... --include='*.html'` used as evidence, which starts matching
`.dev/docs/html/` once the docs have been built in that worktree — an issue's
own generated page can have the searched word in its *filename*. Use `git grep`,
which cannot see the untracked build output, or `--exclude-dir=.dev`.
