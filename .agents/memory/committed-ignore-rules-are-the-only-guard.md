# Keep private state out with committed rules

This note helps contributors add an ignore rule where a fresh clone will see it.

Put a new exclusion in `.gitignore` and in `.containerignore`.
Do not rely on `.git/info/exclude` or a global excludes file; a fresh clone has neither.
Write `/.dev`, not `/.dev/`, when a path may be a symlink.
Write `**/*.sql`, not `*.sql`, in `.containerignore`; a bare pattern there matches only the context root.
Add the path to `PRIVATE` in `kasvimuseo/tests/test_ignore_rules.py`, and the suite checks it in a disposable repository.
Read [task 4](../../docs/tasks/04-track-private-state-exclusions.md), "Review correction on 2026-10-11", for the private settings module coverage.
