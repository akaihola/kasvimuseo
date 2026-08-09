---
name: browser-suite-server-dies-under-sibling-load
description: "A browser-test run that fails with \"Connection refused\" is the host OOM-killing gunicorn, not a test bug"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7f3ae8f7-a1a2-4453-9be7-8cf43dfa13bf
  modified: 2026-08-02T17:41:16.488Z
---

`dev/kasvimuseo app browser-test` runs a gunicorn container for the whole
session. When sibling task workspaces are building images or running their own
suites, the host (11 GB, 4 cores, swap already in use) kills that container with
no SIGTERM — the log stops after "Booting worker" with no "Handling signal:
term", and every test from that point fails with
`Page.goto: Could not connect to 127.0.0.1: Connection refused` or errors in the
`editor` fixture. Assertion failures in the same run (e.g. a drag-geometry
comparison) are suspect too.

**Why:** it reads exactly like a broken change — a whole engine's worth of tests
collapsing at once — and I spent a while looking for a fixture bug that was not
there.

**How to apply:** before diagnosing, `grep -c 'Connection refused'` the log and
check `podman ps` for another workspace's `kasvimuseo-dev-*` container. Re-run
when the machine is quiet; pin `KASVIMUSEO_BROWSER_PORT` and
`KASVIMUSEO_PG_PORT` so two workspaces cannot pick the same ones. See
[[dev-image-tag-is-shared-between-workspaces]] and
[[run-the-suite-in-the-container]].
