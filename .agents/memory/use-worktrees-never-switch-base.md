# Use a task worktree

This note helps contributors isolate task changes from other work.

Use the supplied task worktree when one exists.
Otherwise, create a branch and worktree in an unused directory:

```bash
git worktree add -b task-name /path/to/task-checkout main
```

Replace `task-name` and `/path/to/task-checkout` with your chosen branch and directory.
Keep the base checkout on its current branch.
Check `git worktree list` before creating or removing a worktree.
Check both checkouts for uncommitted changes before merging.
Read [TASKS.md](../../TASKS.md), "Workflow for new issue completion", for integration and cleanup.
