---
name: verify-a-stage-against-the-dump
description: "how Stage 5 verified schema against production — old-code worktree sharing this checkout's cluster via a .dev symlink"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7f3d9cf2-91a2-4684-8f31-6ee78cd7b47f
  modified: 2026-08-09T15:15:05.305Z
---

To run an older stage's migration commands against the current workspace's
database: `git worktree add /tmp/claude/stageNwt <old-commit>`, then
`ln -s $PWD/.dev /tmp/claude/stageNwt/.dev` — the dev script computes
PGDATA/PGSOCK from $REPO, so the symlink makes both checkouts share one
cluster. Select the old image with KASVIMUSEO_IMAGE (Stage 4's is
`kasvimuseo-dev-stage4`: Django 1.6.11 + South; Stage 6's is
`kasvimuseo-dev-stage6`: Django 1.8.19 + photologue 3.4.1) and the target
database with KASVIMUSEO_DB_NAME.

**Why:** a production dump predates Stage 2; only pre-Stage-5 code (with
South) can bring it to the South endpoint before Django-migrations code can
adopt it. Django 1.7's plain `migrate` then auto-fakes the initials (output
says FAKED) — `--fake-initial` is the 1.8+ spelling.

**How to apply:** restore dump with `KASVIMUSEO_DB_NAME=x db restore`, run
`db upgrade-photologue` + `migrate` from the old worktree, then `app manage
migrate` from the new one; compare `information_schema.columns` against a
`db bootstrap` database. Known inherited diffs: `photologue_gallery.title`
and `photologue_photo.title` are varchar(100) vs the model's 50.
Since 2026-08-09 the repo documents all of this itself: the die-message of
`db upgrade-photologue` carries the full worktree recipe, README.rst has the
developer warning ("Development setup") and the production cutover ("Crossing
the South cut", under Deployment), and the Stage 5 record names the 1.7
fake-by-existence trap. Point people there instead of restating.
Related: [[photologue-phantom-makemigrations]], [[dev-image-tag-is-shared-between-workspaces]].
