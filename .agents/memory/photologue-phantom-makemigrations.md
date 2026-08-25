---
name: photologue-phantom-makemigrations
description: makemigrations always proposes a spurious photologue migration (0009 under 3.4.1); migrate is unaffected
metadata: 
  node_type: memory
  type: project
  originSessionId: 7f3d9cf2-91a2-4684-8f31-6ee78cd7b47f
  modified: 2026-08-24T20:25:57.373Z
---

On Django ≥1.7, `makemigrations` always detects cosmetic drift in photologue:
its shipped migrations never match its models. Under photologue 3.0.2 it was
one AlterField (`PhotoEffect.filters` builds `help_text` from the installed
Pillow's filter list); under 3.4.1 (upgrade plan Stage 6, Django 1.8) the
phantom is `photologue/0009_auto_*` altering `photo.date_taken` and
`photoeffect.filters`. It is written into site-packages (ephemeral in the
container) and can be named as a dependency of anything generated beside it.

**Why:** "no pending migrations" cannot be checked with `makemigrations
--dry-run`; use `migrate --list` instead (Django 1.10, on master since
Stage 8, removed it: use `showmigrations`). Any newly generated kasvimuseo
migration may carry a dead `('photologue', '0009_auto_…')` dependency.

**How to apply:** generate scoped — `makemigrations kasvimuseo` — and check
the new file's dependencies name only migrations that exist in the installed
package (3.4.1 ships 0001…0008). Stage 6's `0003_contact_email_length` came
out clean, depending only on `('kasvimuseo', '0002_photo_sizes')`.
Related: [[verify-a-stage-against-the-dump]].
