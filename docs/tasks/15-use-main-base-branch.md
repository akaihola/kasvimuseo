---
depends-on: []
---

# 15. Use `main` base branch

This task is for the maintainer and for contributors with an older clone.
It renames the integration branch from `master` to `main`, and it records what is outside this repository.

- Priority: None.
- Owner: Project maintainer.

## Decisions

The maintainer made these decisions on 2026-10-09:

- Rename the local branch and the GitHub branch.
- Replace every mention of the branch, dated records included.
- Keep a temporary local alias, so that the open task worktrees continue to work.

One mention stays: `AGENTS.md` links to a file on the `master` branch of another project.

## Work

1. Rename the local branch with `git branch -m master main`. Move the `branch.master` section of `.git/config` to `branch.main`.
2. Add the alias `refs/heads/master`, a symbolic reference to `refs/heads/main`.
3. Set `receive.hideRefs` to `refs/heads/master`. A push to the alias then fails, so it cannot move `main` under the base checkout.
4. Replace the branch name in the documentation, the memories, `TASKS.md`, the workflow, `dev/`, `docs/_ext/` and the tests.
5. Rename the GitHub branch with the branch rename API. GitHub then changes the default branch and the base of the open pull requests.
6. Set the upstream of `main` to `origin/main`, and set `origin/HEAD` again.

## Status on 2026-10-09

Steps 1 to 4 are done, in merge `a2d5902`.
The suite (543 tests) and a clean documentation build passed before the merge.

Step 5 failed with HTTP 403, `Resource not accessible by personal access token`.
The token on `gogo` does not have the Administration permission.
The maintainer must rename the branch on `atom`, or in **Settings -> Branches** on GitHub:

    gh api -X POST repos/akaihola/kasvimuseo/branches/master/rename -f new_name=main

Then do step 6 in the base checkout on `gogo`:

    git fetch origin --prune
    git branch -u origin/main main
    git remote set-head origin --auto

## Remove the alias

Remove the alias when no task worktree on this machine uses `master`.
On 2026-10-09 these branches used it: `review/django-6-premerge`, `feature/separate-private-dep-5e9`, and the `feature/upgrade-*` branches.

    git symbolic-ref --delete refs/heads/master
    git config --unset receive.hideRefs

## Outside this repository

- The private deployment repository has memories that name `master` of this repository. Its owner must change them.
- At the last fetch, the `bitbucket` remote had a `master` branch. Rename it in the Bitbucket settings, or remove the remote.
- An older clone needs these commands:

        git branch -m master main
        git fetch origin --prune
        git branch -u origin/main main
        git remote set-head origin --auto

## Completion checks

- [ ] `git symbolic-ref HEAD` in the base checkout prints `refs/heads/main`.
- [ ] `git grep -w master` finds only `AGENTS.md`, this description, and the alias memory with its line in `MEMORY.md`.
- [ ] The application suite and a clean documentation build pass on `main`.
- [ ] The GitHub default branch is `main`, and pull requests 1 and 2 have `main` as their base.
