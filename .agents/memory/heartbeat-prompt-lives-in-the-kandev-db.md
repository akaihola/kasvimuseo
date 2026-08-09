---
name: heartbeat-prompt-lives-in-the-kandev-db
description: "The Kandev `heartbeat` prompt is a DB row, not a repo file; edit it with sqlite3 and expect a cache"
metadata: 
  node_type: memory
  type: project
  originSessionId: d5873896-0395-4511-a7f3-53d5588c6ff8
  modified: 2026-08-04T20:44:52.234Z
---

The `heartbeat` prompt is row `c329c523-07f6-4fd7-bd59-a66d2b6566cf` of the
`custom_prompts` table in `~/.kandev/data/kandev.db`. Grepping the repository
for "heartbeat" finds nothing. `merge` and the builtin prompts live in the same
table.

**Why:** it is outside git, so a repo change cannot alter agent behaviour on its
own, and the change is not reviewable in a diff.

**How to apply:** put durable rules in `AGENTS.md` (the repo file every session
loads) and keep the DB prompt as a pointer to it. To edit the row, back the
database up first and write with `python3` + `sqlite3`; the sandbox blocks
writes to `~/.kandev/data`, so that call needs the sandbox off. Kandev may serve
the old text until it restarts. See [[no-github-push-from-here]] for the other
half of "cannot be validated in CI".
