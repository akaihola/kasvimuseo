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

- [ ] git check-ignore accepts the supported private files and links using only committed rules.
- [ ] git add --dry-run does not select those paths.
- [ ] Required public examples remain trackable, and supported container contexts exclude private files.

## Related work

Package-content protection remains the responsibility of [proposal 01](01-exclude-private-settings-from-packages.md).
