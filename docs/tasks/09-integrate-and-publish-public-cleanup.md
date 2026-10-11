---
depends-on: [1, 2, 3, 4, 5, 6, 7, 8]
---

# 09. Integrate and publish the public cleanup

This proposal helps the maintainer deliver the reviewed cleanup to contributors through the public integration branch.

- Priority: High.
- Proposed owner: Project maintainer.

## Proposed work

1. Locate the prepared cleanup and compare it with current integration changes.
2. Preserve unrelated work when preparing the final changes.
3. Resolve the content, packaging, and documentation proposals in this register.
4. Run the required application checks and a clean documentation build on the final tree.
5. Inspect the release artifacts before publication.
6. Commit, integrate, and publish the accepted cleanup.
7. Check the result through a fresh clone and newly generated documentation.

## Review evidence

The review assessed uncommitted cleanup changes. The supplied review checkout and the public integration branch still contained the earlier tree.
A separate prepared checkout and base checkout also contained different unrelated edits.

## Completion checks

- [ ] A fresh public clone contains the accepted cleanup.
- [x] Required checks pass against the integrated revision.
- [ ] Published packages and documentation match that revision and pass the content checks.
- [ ] The maintainer records any remaining publication or history work in the appropriate private records.

## Dependencies

Complete proposals 01 through 08 before declaring the public cleanup ready. Coordinate external publication work with the maintainer.

Update of 2026-10-06: local `main` contains the cleanup as merge `9e211ab`, so step 1 is done.
Do not do step 6 before the private deployment repository completes tasks 1, 3, and 4.
Task 1 publishes the deployment repository to a private remote. Task 3 rotates the exposed credentials. Task 4 removes sensitive public history.
After private task 4 replaces history, repair the `:Resolution:` commit references before the documentation build in step 4.

## Work done on 2026-10-11

Private tasks 1, 3, and 4 are accepted. Private task 9 holds the rewritten history and is still in progress.
The prepared clean `main` is `0ea0730`, rewritten from the `main` snapshot `03755f2`.
Its commit map lives in the private deployment repository under `.local/history-rewrite/20261010-185939-task-9/`.

1. We reran `bin/rewrite-public-history` from the private repository against the current `main` into a temporary directory. All 899 shared commits received the same hashes as the prepared map, so the repair can use the prepared map.
2. We rewrote every commit hash in `docs/` and `docs/tasks/` with the map: 140 checked pointers and the hashes in prose, in 85 files.
3. Issue 025 named a dropped commit that only changed a removed deployment issue file. Issue 082 named a dropped commit that only changed `ansible/install.yaml`. Both `:Resolution:` fields now say that the private deployment repository keeps those records.
4. Issue 062 keeps its pointer at the rewritten spike commit `72b65c4`, on the rewritten tag `interim-062-option-2`. The publication must include that tag, or the documentation build fails in a fresh clone.
5. The task description `docs/tasks/02` names a commit that is on no surviving branch. We left it, because the build does not check task descriptions.
6. We fetched the rewritten `main` and the rewritten interim tag into `refs/clean/` in the shared repository. Read `.agents/memory/fetch-the-clean-history-before-the-docs-build.md`.

Step 6, the publication, waits for the maintainer. The agent token cannot push a history that changes `.github/workflows/`, and private task 9 must end first.

## Validation on 2026-10-11

- `dev/repoint --verbose` in this worktree: 138 pointers, 137 landed and 1 parked, after the fetch into `refs/clean/`.
- `dev/kasvimuseo docs --clean` built `.dev/docs/html/index.html` with no warning in `.dev/docs/build.log`.
- `dev/kasvimuseo app test` in the `kasvimuseo-dev-task9` image: 585 passed in 22 seconds.
- `git diff --check` passed.
- We rewrote this branch with `bin/rewrite-public-history` into a temporary bare repository. The scan passed: no denied path, no exposed value, no vault blob or host name in 871 commits.
- In a fresh clone of that result, `dev/repoint` reported 137 landed and 1 parked, the clean documentation build passed, and `python3 setup.py sdist bdist_wheel` produced the two artifacts. `dev/check-release-artifacts` reported that both carry no private settings.

## What is still open

- Step 6, the publication: the maintainer pushes the rewritten `main` with an account that permits workflow changes, after this merge and a final rewrite. The push must include the tag `interim-062-option-2` next to `0.2.0`, because issue 062 names a commit on that tag. Read the private `docs/public-history-cleanup.rst`, "Rewrite procedure".
- Step 7 against GitHub: a fresh public clone, a documentation build on it, and the published documentation check wait for that push.
- The first, third and fourth completion checks stay open until the maintainer publishes.
