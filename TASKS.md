# Issue tracking for Kasvimuseo

Rules for TASKS.md usage are at the bottom of the file.
This file is for the maintainer and the contributors who pick up work.
It sets the order of the open work.
The maintainer verified the proposals of the repository review of 2026-10-04 on 2026-10-06.
Tasks 10, 11, 12, and 14 come from the integration of the deployment split and the Django 6.0 upgrade.
Task 13 carries over the open iPad checks of issue 056.
On 2026-10-07 the maintainer decided that the iframe loader deduces the catalogue origin without `data-site-url`; task 5 carries that.

## Unverified proposals

## Ordered backlog

- [3] Replace operational data and personal examples
    - Depends on: [10]

- [7] Preserve vendored dependency license notices

- [8] Refresh public documentation after the repository split
    - Depends on: [2], [3], [5], [6], [7], [10]

- [4] Track exclusions for private local state

- [16] Move the images and the locks to Python 3.13
    - Depends on: [10], [11]

- [14] Close the runtime upgrade programme (issue 036)
    - Depends on: [10]

- [9] Integrate and publish the public cleanup
    - Depends on: [1], [2], [3], [4], [5], [6], [7], [8]

- [13] Finish the iPad label checks (issue 056)

- [12] Decide how to handle the rotation regression in photo effects (issue 089)
    - Depends on: [10]

## Scheduled

- [6] Declare the project license
  <!-- hai:{"updatedAt":"2026-10-10T18:28:18.805Z"} -->

- [11] Move the browser tests to Playwright 1.63
  <!-- hai:{"updatedAt":"2026-10-10T18:19:18.837Z"} -->

## In Progress

- [~] [1] Exclude private settings from release packages
  <!-- hai:{"updatedAt":"2026-10-10T18:19:53.455Z"} -->

- [~] [5] Deduce the catalogue origin in the iframe loader
  <!-- hai:{"updatedAt":"2026-10-10T18:08:23.828Z"} -->

- [~] [10] Integrate the Django 5.2 and 6.0 upgrade

## Completed / Accepted

- [ ] [2] Keep contributor memories portable
  <!-- hai:{"updatedAt":"2026-10-10T18:28:02.595Z"} -->

- [x] [15] Use `main` base branch
  <!-- hai:{"id":"simple-62a534f6-9f9d-4252-8c7a-eb3b68ad8167","priority":"none","labels":[],"createdAt":"2026-10-06T19:33:17.859Z","updatedAt":"2026-10-10T09:18:34.698Z"} -->

[1]: docs/tasks/01-exclude-private-settings-from-packages.md
[2]: docs/tasks/02-keep-contributor-memory-portable.md
[3]: docs/tasks/03-replace-operational-data-and-personal-examples.md
[4]: docs/tasks/04-track-private-state-exclusions.md
[5]: docs/tasks/05-document-and-test-iframe-origin-configuration.md
[6]: docs/tasks/06-declare-project-license.md
[7]: docs/tasks/07-preserve-vendored-license-notices.md
[8]: docs/tasks/08-refresh-public-documentation.md
[9]: docs/tasks/09-integrate-and-publish-public-cleanup.md
[10]: docs/tasks/10-integrate-the-django-5-2-and-6-0-upgrade.md
[11]: docs/tasks/11-move-the-browser-tests-to-playwright-1-63.md
[12]: docs/tasks/12-decide-the-photo-effect-rotation-regression.md
[13]: docs/tasks/13-finish-the-ipad-label-checks.md
[14]: docs/tasks/14-close-the-runtime-upgrade-programme.md
[15]: docs/tasks/15-use-main-base-branch.md
[16]: docs/tasks/16-move-the-images-and-locks-to-python-3-13.md
[*]: TASKS.md

<!-- hai:reserved-numbers:1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16 -->

---

## Rules

Here are the rules for TASKS.md usage:

### TASKS.md maintenance sessions

- In `## Completed / Accepted`, `- [ ] [N] summary` or `- [ ] [*] summary` means
  completed work awaiting user acceptance. `- [x] [N] summary` or `- [x] [*] summary`
  means the user has accepted it. Only user acceptance changes `[ ]` to `[x]`;
  completion, tests and deployment do not.
- Move newly completed issues into `## Completed / Accepted` with `[ ]`.
- During the next maintenance run, remove only `[x]` issues from this section, plus
  their unused description files and reference-style links. Keep `[ ]` issues and any
  files or links still referenced by another issue.
- Each issue must retain either
    - a numbered reference-style link (e.g. `[1]`) to a description file, or
    - `[*]` to indicate no description file is needed for a simple task.
- `[~]` marks an issue that is actively in progress. When the issue is complete, move it
  to `## Completed / Accepted` with `[ ]`, pending user acceptance.
- Link references are listed between `## Completed / Accepted` and `## Rules`.
- Keep summaries concise. Move detailed requirements, rationale, examples and acceptance
  criteria into `docs/tasks/N-issue-description.md`; preserve simple tasks inline. Reuse
  an existing description for the same issue.
- For a new description, use the first unused number, checking both this file and
  description filenames in available Git history. Do not reuse numbers of accepted
  issues.
- Preserve Hai metadata comments during manual edits, including the reserved-number
  ledger that prevents identifier reuse after cleanup without Git history.
- The section records work status; the checkbox in `## Completed / Accepted` records
  user acceptance. Completed descriptions retain historical requirements, paths and
  validation results; they are not current implementation instructions. Date later
  corrections and distinguish regressions from earlier work.
- Any completed tasks which haven't yet been moved from `## In Progress` to
  `## Completed / Accepted` should be moved there.
- Any in progress tasks which haven't yet been moved from `## Ordered backlog` or
  `## Scheduled` to `## In Progress` should be moved there.
- Ensure there are no duplicate sections, and that they are in the correct order:
  `## Unverified proposals` -> `## Ordered backlog` -> `## Scheduled` ->
  `## In Progress` -> `## Completed / Accepted` -> `## Rules`.

### Modifying issues

- Ensure dependencies between issues are correctly updated.
- State dependencies using
    - indented `- Depends on: [N]` bullets in TASKS.md, and
    - YAML frontmatter in description files.
- Ensure backlog order respects dependencies.
- When you move an issue, preserve its identifier, text and line wrapping. Change only
  the status checkbox when completion or user acceptance requires it. This keeps moves
  identifiable in Git and reduces avoidable conflicts.

### Workflow for new issue completion

Git operations below apply only when this directory is a Git repository. Without Git,
use the working files, skip branch/commit/rebase/merge steps, and preserve the same
scheduling, implementation, validation, and acceptance transitions. Do not initialize a
repository just to satisfy these rules.

Below, `<filename>@<branch>` means operate on the file in the specified branch.

1. Choose issue and schedule work

- Pick the first issue in `TASKS.md@main` with no dependency on uncompleted work.
- Move it from `## Ordered backlog` to `## Scheduled` in `TASKS.md@main`, and commit
  when the Git workflow applies.

2. Work on the issue

- Move the issue to `## In Progress` in `TASKS.md@<worktree-branch>`, mark it `[~]`, and
  ensure no copy is left in the backlog or scheduled section.
- Create or update, review and refine `docs/tasks/N-issue-description.md` if the plan
  needs more than a concise bullet. Link a new description with a new `[N]`.
- Reword the summary if needed. Commit the description and tracker when applicable.
- Implement, test, review, and refine the work in the feature worktree when available.

3. Merge and deploy

- When Git applies, rebase the feature branch on `main`, resolve conflicts, merge it,
  and remove the worktree and branch.
- Move the issue to `## Completed / Accepted` with `[ ]`, pending user acceptance, and
  commit when applicable.
- Follow any release steps in `README.rst`.
