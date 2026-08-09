---
name: stale-dev-image-looks-like-a-missing-jqm
description: "ImportError: No module named jqm from the suite or any manage command means the kasvimuseo-dev image tag is stale, not that a dependency is missing"
metadata: 
  node_type: memory
  type: project
  originSessionId: b6a58810-c6e5-469b-bf23-36c28bea9ec0
  modified: 2026-08-01T10:19:02.912Z
---

If `dev/kasvimuseo app test` or any `app manage` command dies with
`ImportError: No module named jqm`, the `kasvimuseo-dev` image tag is pointing
at an old layer. `django-jqm` is in `requirements/production.txt` and installs
fine; the fix is `dev/kasvimuseo app build`, which re-tags `kasvimuseo-dev` from
cached layers in seconds.

**Why:** the failure reads as a broken dependency, and chasing it into
`pip list` inside `podman run --rm kasvimuseo-dev` reproduces it, which makes
the wrong diagnosis look confirmed — the same stale tag is what that command
runs.

**How to apply:** rebuild the image before concluding anything about
dependencies, and note that `manage.py` prints only the last line of such an
error (`BaseCommand.execute` swallows the traceback), so the one-line message is
all the evidence there is. Related: [[run-the-suite-in-the-container]].
