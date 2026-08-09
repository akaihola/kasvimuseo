---
name: repoint-repairs-rebased-hashes
description: "dev/repoint re-points a :Resolution: hash after the rebase; the docs build now tests reachability, not object existence"
metadata: 
  node_type: memory
  type: project
  originSessionId: a2d7dffe-ead6-466a-b9f9-ab297259e1ff
  modified: 2026-08-05T19:04:49.362Z
---

Since 2026-08-05 kasvimuseo allows a branch-local commit hash in a
`:Resolution:` field, and repairs it afterwards instead of forbidding it. The
landing sequence is: `git rebase master`, then `dev/repoint` (report), then
`dev/repoint --write`, commit, then merge `--no-ff`.

`dev/repoint` maps a dead hash to what landed, best source first: the
`.git/rewritten-commits` log written by the `dev/post-rewrite` hook, then
`git patch-id --stable` against master, then the commit subject. It refuses to
guess — a squashed or split commit is reported for a person.

`docs/_ext/commit_pointers.py` holds the logic; the Sphinx check and the CLI
both drive it, and `kasvimuseo/tests/test_commit_pointers.py` tests it with a
fake `git` (so it runs in the Python 2.7 container). See
[[resolution-hash-dies-in-the-rebase]] for the trap it exists for.

**How to apply:** three traps are now encoded in the code, and worth
remembering because they each read as "the check works" when it does not.
Existence is not reachability — use `git merge-base --is-ancestor`. A checkout
with no local `master` (CI clones one branch and keeps `origin/master`) used to
skip the check silently. And an all-digit abbreviation like `7200893` is
invisible to the register's hash regex, which requires a digit *and* a letter,
so the tool lengthens such a hash until it reaches a letter.
