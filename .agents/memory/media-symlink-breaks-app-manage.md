---
name: media-symlink-breaks-app-manage
description: "kandev worktrees' media symlink breaks `app manage` in the container since photologue 3.4 writes at import"
metadata: 
  node_type: memory
  type: project
  modified: 2026-08-09T15:14:51.678Z
  originSessionId: 55b904c9-6cab-4639-b913-8cb3a763a366
---

In kandev task worktrees, `media` is an untracked, gitignored symlink to
`../../../../prg/kasvimuseo/media` (the base checkout's 278 MB). Inside the
container the relative target escapes the `/src` mount, so the symlink is
broken there. photologue ≥3.4 writes `photologue/photos/cache/CACHEDIR.TAG`
into MEDIA_ROOT at *import* time, so from upgrade plan Stage 6 on, every
`dev/kasvimuseo app manage …` in such a worktree dies with
`OSError: /src/media/photologue`. `app test` is unaffected (tmpdir
MEDIA_ROOT fixture).

**Why:** the failure looks like a photologue packaging bug; it is the
workspace's symlink. `git checkout -- media` cannot restore it — the file is
not tracked (`git check-ignore media` printing "media" means ignored, not
tracked).

**How to apply:** for manage runs, `rm media && mkdir media`, work, then
`rm -rf media && ln -s ../../../../prg/kasvimuseo/media media` to restore.
Related: [[verify-a-stage-against-the-dump]], [[no-ssh-to-production]].
