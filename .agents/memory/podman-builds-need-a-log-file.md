---
name: podman-builds-need-a-log-file
description: "Build images with output to a log file and wait for \"Successfully tagged\" — a backgrounded build can end silently and leave a stale or dangling tag"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5fe7a285-761d-4c13-8279-89c5b962ebef
  modified: 2026-08-02T10:53:22.203Z
---

Two `podman build` runs started with `run_in_background` and piped through
`tail` ended with empty output and exit code 0 during upgrade Stage 2; one left
`localhost/kasvimuseo-dev` untagged (the image was present as `<none>`, and
`podman tag <id> kasvimuseo-dev` restored it), and a later `podman run` of the
production tag used the *previous* image because the tag had not moved yet.
Redirecting to a file (`dev/kasvimuseo app build > /tmp/claude/build.log 2>&1`)
and waiting on the log worked every time.

**Why:** the harness notification cannot tell a half-finished build from a
successful one, so the next command silently runs against the wrong packages --
which reads as a dependency bug (see
[[stale-dev-image-looks-like-a-missing-jqm]]) or as a fix that did not take.
A sibling workspace rebuilding the same tag does the same thing
([[dev-image-tag-is-shared-between-workspaces]]).

**How to apply:** redirect image builds to a log file, wait for
`Successfully tagged`, then confirm with `podman run --rm <image> pip list`
before trusting any result that depends on the new packages.
