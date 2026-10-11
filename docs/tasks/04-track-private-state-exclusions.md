---
depends-on: []
---

# 04. Track exclusions for private local state

This proposal helps contributors prevent accidental commits of private state and compatibility links in fresh checkouts.

- Priority: Medium.
- Proposed owner: Development tooling maintainer.

## Proposed work

1. Add project ignore rules for both a .dev directory and a .dev symlink.
2. Exclude .claude/settings.json and other supported machine-specific configuration paths.
3. Audit container build exclusions against the supported container tools.
4. Check the rules in a disposable repository without global or local Git exclusions.

## Review evidence

The review found that `.git/info/exclude` supplies protection missing from [.gitignore](../../.gitignore).
The tracked `/.dev/` pattern does not exclude a symlink named `.dev`. The tracked rules also omit `.claude/settings.json`.

## Completion checks

- [x] git check-ignore accepts the supported private files and links using only committed rules.
- [x] git add --dry-run does not select those paths.
- [x] Required public examples remain trackable, and supported container contexts exclude private files.

## Work done on 2026-10-10

1. `.gitignore` ignores `/.dev` without a trailing slash, so a symlink named `.dev` is ignored too. It ignores the whole `.claude/` directory, `.mcp.json`, `.vscode/`, and `ylaneenkasvit/local_settings.*.py`.
2. `.containerignore` is the file Podman reads, and Podman is the supported build tool (`README.rst`, "Development setup"). It now excludes `.dev` as a symlink, `.worktrees/`, `.githooks/`, `.mcp.json`, `.vscode/`, and `.idea/`.
3. The audit found that a bare `*.sql` in `.containerignore` matches only at the context root. The dump, `.env`, and bytecode rules now start with `**/`.
4. `kasvimuseo/tests/test_ignore_rules.py` builds a disposable repository with the tracked `.gitignore` alone, once with a `.dev` directory and once with a `.dev` symlink. It runs `git check-ignore` and `git add --dry-run` there, and applies `.containerignore` with the Podman matching rules.
5. `dev/Containerfile` installs `git`, so the checks run inside the development image with the rest of the suite.
6. `README.rst`, "Development setup", names the two files and the test. `.agents/memory/committed-ignore-rules-are-the-only-guard.md` records the two pattern traps.

The machine-specific settings modules stay in `ylaneenkasvit/`; `setup.py` excludes them from packages (proposal 01).

## Validation on 2026-10-10

- The nine new tests pass on the host and in the development image.
- A throwaway Podman build copied a planted context with every private path and a `.dev` symlink. With the new rules the image held none of them and held every file the production `Dockerfile` copies.
- The same build with the old rules held `backups/production.sql`, `.mcp.json`, `.vscode/settings.json`, `.idea/workspace.xml`, `.worktrees/task/README.rst`, and two `.pyc` files.

## Review correction on 2026-10-11

The independent review found that Git still selected underscore and numeric settings variants.
`.gitignore` now uses `/ylaneenkasvit/local_settings*.py`, matching the private module family excluded by packages and container builds.
The tests cover both variants and confirm that `development_settings.py` remains trackable.

## Validation on 2026-10-11

- The expanded tests failed four Git checks before the rule changed.
- All nine focused tests passed on the host and in the existing Python 3.13 development image.
- `git diff --check` and `dev/kasvimuseo docs --clean` passed.

## Related work

Package-content protection remains the responsibility of [proposal 01](01-exclude-private-settings-from-packages.md).
