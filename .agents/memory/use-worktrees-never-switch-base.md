---
name: use-worktrees-never-switch-base
description: Do task work in a git worktree kept inside the repo; never change the branch of the base repo checkout
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1354338d-a46e-4551-80fc-474bdcb5aa35
  modified: 2026-07-31T05:23:11.037Z
---

Do all task work in a git worktree. Never run `git checkout <branch>` in the
base repo checkout at `~/prg/<repo>` — leave it on whatever branch it is on.

**Keep worktrees INSIDE the main repository**, in every project. Use
`.claude/worktrees/<name>`, which is where the `EnterWorktree` tool creates them
with no configuration; gitignore that path. `.worktrees/` is the equivalent when
adding one by hand — precedent: `~/prg/git-knit/.gitignore`.

**Exception: when a harness already provisioned the worktree, use it as-is.**
Kandev starts sessions in `~/.kandev/tasks/<task>_<id>/<repo>`, outside the repo.
Do not relocate it — it satisfies the rule's intent: the base checkout keeps its
own branch, and the sandbox grants write access to both that cwd and
`~/prg/<repo>/.git` (where its gitdir points), so file and git-ref writes work.
Verified 2026-07-29 in kasvimuseo.

Do **not** use the sibling `~/prg/<repo>-worktrees/<name>` layout for anything
new, even though `~/prg/pykoclaw-worktrees/*` and `~/prg/mitto-voice-worktrees/*`
still use it. Those and `~/prg/kasvimuseo-worktrees/*` were left in place
deliberately; the rule applies going forward only.

**Why:** other agents and tools operate on the base checkout concurrently. During
one session it was switched between three branches by something outside the
conversation, which silently moved work-in-progress out from under the agent.
A worktree gives the task its own working directory and branch, immune to that.
Keeping it inside the repo also keeps it in the sandbox's writable root, which
the sibling layout does not — see the gotchas below.

**How to apply:** prefer `EnterWorktree`. By hand:
`git worktree add .claude/worktrees/<name> <branch>`. The branch must not be
checked out in the base repo first, so if the base is sitting on it, move the
base back to `master`/`main` before adding the worktree. Gotchas:

- `git worktree add -b <name>` **creates the branch even when it then fails**.
  A retry dies with "a branch named … already exists"; `git branch -D <name>`
  first.
- Anything outside the repo root — creating a sibling `-worktrees/` directory,
  or touching the base checkout after `EnterWorktree` moved the session — needs
  `dangerouslyDisableSandbox: true`. Worktrees inside the repo avoid this.

Rebase task branches onto `master`; never merge `master` into them. Merge the
finished branch back with `--no-ff` (see `~/.config/coding-agents/git.md`).

**Merging back does not need a checkout switch**, because the base repo is
already sitting on `master`: run `git -C ~/prg/<repo> merge --no-ff <branch>`
from the worktree. It needs `dangerouslyDisableSandbox: true` — the sandbox
allows `~/prg/<repo>/.git` but not the base *working tree*, so the sandboxed
attempt dies with `unable to unlink old '<file>': read-only file system` for
every file the merge touches. That failure is clean: the merge aborts and the
base checkout is left untouched, so just retry with the sandbox off.
Verified 2026-07-31 in kasvimuseo.
