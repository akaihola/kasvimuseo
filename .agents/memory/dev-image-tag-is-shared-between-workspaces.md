---
name: dev-image-tag-is-shared-between-workspaces
description: "kasvimuseo-dev is one podman tag for every task worktree, so a sibling agent's build silently replaces yours"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e009c59-ef05-4656-9528-fb2acb4b267e
  modified: 2026-08-02T10:44:24.498Z
---

`dev/kasvimuseo` uses `IMAGE=${KASVIMUSEO_IMAGE:-kasvimuseo-dev}`, and every
task worktree on this machine builds that same tag. A sibling task on an
upgrade branch (photologue 2.8.3) rebuilt it mid-session on 2026-08-02 and my
`app browser-test` started failing with
`photologue.gallery: 'sites' has an m2m relation with model Site, which has
either not been installed or is abstract` -- 2.8's `sites` m2m against an
`INSTALLED_APPS` that has no `django.contrib.sites`. Nothing on my branch was
wrong, and it reproduced on a clean `git stash`, which looks exactly like a
pre-existing master failure.

**Why:** the symptom is a validation error in the application, not a container
error, so it reads as a code problem.

**How to apply:** if the container's packages disagree with
`requirements/production.txt` (`podman run --rm kasvimuseo-dev pip freeze`),
build a private tag and pass it to every invocation:

    podman build -f dev/Containerfile -t kasvimuseo-dev-<slug> .
    KASVIMUSEO_IMAGE=kasvimuseo-dev-<slug> dev/kasvimuseo app test

`podman images` timestamps show who built what. Related:
[[run-the-suite-in-the-container]], [[stale-dev-image-looks-like-a-missing-jqm]].
