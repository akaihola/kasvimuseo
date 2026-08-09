---
name: sandbox-reaps-detached-processes
description: Processes detached from a Bash tool call (setsid + nohup) are killed when the call ends in this sandbox
metadata: 
  node_type: memory
  type: project
  originSessionId: 56726bbd-b7d4-42d5-bf80-9e85416d888b
  modified: 2026-07-28T09:16:34.936Z
---

In this sandboxed agent environment, a process started from the Bash tool with
`setsid nohup ... >/dev/null 2>&1 </dev/null &` is killed shortly after the tool
call returns — verified 2026-07-28 with both a bare `sleep 25` marker test and a
40-second `sphinx-build`, which died mid-run every time.

**Why:** background work that must outlive a tool call cannot rely on detaching;
long jobs need `run_in_background: true` (harness-tracked) instead.

**How to apply:** for a hook that must not block the agent, use the settings.json
`"async": true` flag on the command hook and run the work in the *foreground* of
the hook process — the harness then owns it and does not reap it. Verified
working for `dev/docs-hook` → `dev/docs-build` on 2026-07-28. Still make such
work resumable and idempotent (marker file while running, cleared on success, so
the next trigger finishes an interrupted run).
