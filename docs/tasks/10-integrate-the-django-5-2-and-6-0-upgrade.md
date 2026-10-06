---
depends-on: []
---

# 10. Integrate the Django 5.2 and 6.0 upgrade

This task helps the maintainer land the finished runtime upgrade and remove the branches that it replaces.

- Priority: High.
- Owner: Project maintainer. A merge into `master` needs the maintainer's approval.

## Work

1. Merge `review/django-6-premerge` into local `master` with `git merge --no-ff`.
2. Run the application suite, the coverage gate, and a clean documentation build on the merge result.
3. Remove the branches that the merge replaces: `feature/upgrade-to-django-5-530`, `feature/upgrade-django-to-6-0ao`, and `feature/separate-private-dep-5e9`. Remove their task worktrees too.
4. Delete `refs/backup/base-worktree-2026-10-05` and `refs/backup/review-django-6-premerge-pre-rebase` when nobody needs them.

## Evidence

The branch holds issues 087 and 088, which move the runtime to Django 5.2.16 and then 6.0.7.
It also holds issue 089 and the upgrade plan updates.
It sits directly on the deployment split merge, `ea274ee`.

On 2026-10-05 the branch passed these checks:

- 547 application tests, and the coverage gate at 99.52 %;
- a clean documentation build;
- all 36 Chromium browser checks;
- a production image check of packages, settings, templates, and static files.

One WebKit check failed because of a browser update. Task 11 owns that failure.

## Completion checks

- [ ] `master` contains the upgrade, and `git branch --no-merged master` lists none of the replaced branches.
- [ ] The application suite and a clean documentation build pass on `master`.
- [ ] `docs/upgrade-plan.rst` shows every stage as done.
