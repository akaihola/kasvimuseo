---
name: master-is-an-alias-for-main
description: "Since 2026-10-09 local master is a symbolic ref to main, kept for old task worktrees; pushes to it are refused"
metadata:
  type: project
---

On 2026-10-09 task 15 renamed the integration branch to `main`. In the base
checkout, `refs/heads/master` is now a symbolic reference to `refs/heads/main`,
so `git rebase master` in an old task worktree still works. The setting
`receive.hideRefs=refs/heads/master` refuses a push to the alias. Without it, a
push would move `main` and leave the base checkout's working tree behind.

**Why:** several task worktrees on this machine were cut before the rename, and
their instructions and their copy of `docs/_ext/commit_pointers.py` name `master`.

**How to apply:**

- Write `main` in new work. Do not treat `master` as a second branch.
- Remove the alias as `docs/tasks/15-use-main-base-branch.md` says, when no
  worktree needs it.
- `git branch -m` and `git config` in the base checkout need the sandbox off.
  The sandbox protects `.git/config`. `git branch -m` then renames the branch
  but fails on the config, with `could not lock config file .git/config`.

Related: [[kasvimuseo-integration-branch-is-main]], [[use-worktrees-never-switch-base]].
