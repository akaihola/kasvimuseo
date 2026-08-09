---
name: no-ssh-to-production
description: "No SSH to kasvit.ambitone.com, but the production dump and full media are already on disk in the BASE checkout"
metadata:
  node_type: memory
  type: project
  originSessionId: 043fdf21-c138-41bf-8fb9-bdd177863a80
  modified: 2026-07-31T07:30:05.602Z
---

`agent@gogo`'s key is not authorised on `kasvit.ambitone.com` (vps763955.ovh.net).
Every account tried — `kasvimuseo`, `ylaneenkasvit`, `akaihola`, `agent`, `root` —
returns `Permission denied (publickey,password)`. `atom`, the machine with SSH reach
to production, is also unreachable from here (host key verification failed).

**Why:** `dev/kasvimuseo db fetch` and the README's sshfs media mount both depend on
production SSH, so they cannot be exercised from this account.

**How to apply:** don't retry SSH, and **don't assume there is no dump** — the user
copied one over on 2026-07-27 and it is still there. Check the **base checkout**
before concluding anything is unavailable (confirmed 2026-07-30):

    /home/agent/prg/kasvimuseo/.dev/backups/production.sql   # 17 MB, 156 species
    /home/agent/prg/kasvimuseo/media/                        # 278 MB, 397 real photos

A task worktree has its *own* empty `.dev/backups` and near-empty `media/`, which is
what makes this easy to miss — see [[use-worktrees-never-switch-base]]. To use them
from a worktree, restore by absolute path and copy (do **not** `ln -s ... media`,
which lands as `media/media` because the directory already exists, and a symlink out
of the repo is invisible inside the container anyway):

    dev/kasvimuseo db restore /home/agent/prg/kasvimuseo/.dev/backups/production.sql
    cp -r /home/agent/prg/kasvimuseo/media/photologue/. media/photologue/

**The dump is older than the code — always `dev/kasvimuseo app manage migrate`
straight after `db restore`.** Without it the species list, the observation page and
the species/planting admin change lists answer 500 with `column
kasvimuseo_species.photo_is_horizontal does not exist` (issue 011's migration, and
any later one). Confirmed 2026-07-31: same pages all 200 once migrated. Easy to
misread as a regression from whatever you just changed.

This is what turns "verified the migration against the schema shape" into "verified
it against production data". Fall back to `dev/kasvimuseo db bootstrap` (empty DB
from the migrations) only when the dump genuinely is not there.

Photos need no SSH either way: `media.kasvit.ambitone.com` serves them publicly, so
`dev/kasvimuseo media fetch` downloads the ones the database references over HTTPS.
Only a full mirror of `/www/ylaneenkasvit/media` (material no row points at) needs
rsync or sshfs.
