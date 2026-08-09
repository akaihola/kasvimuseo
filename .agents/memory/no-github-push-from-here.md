---
name: no-github-push-from-here
description: "Pushing to github.com/akaihola/kasvimuseo is denied 403 from this machine, so no agent-run CI or PR"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2b3eb004-096d-424b-9bb7-a7269b794f98
  modified: 2026-08-01T02:57:57.398Z
---

`git push origin <anything>` to `https://github.com/akaihola/kasvimuseo.git`
fails with `remote: Permission to akaihola/kasvimuseo.git denied to akaihola` /
HTTP 403, both with the ambient credential helper and with
`git -c credential.helper='!gh auth git-credential'`. The `gh` PAT can read the
repo (`gh repo view`, `gh api`) but not write it. `origin/master` is also behind
local `master`, so work merged here has not reached GitHub.

Consequence: an agent cannot open a PR, cannot trigger `.github/workflows/tests.yml`,
and cannot report a real CI run — commit locally and say so. Validate workflow
changes with `nix-shell -p actionlint` (needs the sandbox off) plus running the
job's own command locally instead.

**Why:** a task that asks for "the actual workflow run result" is unreachable
from here; claiming one would be a fabrication.

**How to apply:** verify what can be verified locally, then report the blockage
and that a push from `akaihola@atom` is needed. See
[[use-worktrees-never-switch-base]] and [[run-the-suite-in-the-container]].
