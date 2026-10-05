---
name: ready-now-may-be-done-on-a-branch
description: "master's Ready-now queue can list issues already finished on unmerged branches; run git branch --no-merged master before starting one"
metadata:
  node_type: memory
  type: project
  originSessionId: 87f64b48-a4c7-4f91-838f-c76ea9bc9d92
  modified: 2026-10-05T12:34:02.173Z
---

Because merges to master are gated ([[merge-to-master-is-gated]]), finished
task branches pile up unmerged, and their `:Claimed:`/`Fixed` edits are
invisible on master. On 2026-10-05 master listed 087 (Django 5.2) as Open and
unclaimed, but `feature/upgrade-to-django-5-530` had finished it and
`feature/upgrade-django-to-6-0ao` had also finished 088 (Django 6.0) on top.

**Why:** redoing 087 from master would have duplicated a finished upgrade.

**How to apply:** before taking a Ready-now row, run
`git branch --no-merged master` and `git log master..<branch>` for each branch
listed, and read the issue file on the newest branch. Stack new work on the
newest finished branch (as `review/django-6-premerge` did), not on master. Also
check `git status` in the base checkout: on 2026-10-05 it held another task's
uncommitted private-deployment refactor, and that refactor collides with
`docs/issues/index.rst`.
