---
depends-on: []
---

# 02. Keep contributor memories portable

This task helps contributors retain reusable project knowledge while removing machine-specific records from public documentation.

- Priority: Medium.
- Proposed owner: Documentation maintainer.

## Proposed work

1. Review every tracked agent memory, including its metadata.
2. Transfer machine-specific records to private storage before removing them from public source.
3. Keep general development guidance and replace local assumptions with portable instructions.
4. Remove obsolete index entries and check the remaining links.

## Review evidence

The review found local checkout paths, unrelated project names, session identifiers, host capacity, and sandbox-specific instructions in retained memories.

Start with [.agents/memory/MEMORY.md](../../.agents/memory/MEMORY.md), [worktree guidance](../../.agents/memory/use-worktrees-never-switch-base.md), and [resource troubleshooting](../../.agents/memory/browser-suite-server-dies-under-sibling-load.md).

## Completion checks

- [ ] Public memories explain project behavior without identifying a particular machine or private workspace.
- [ ] Each remaining memory link resolves.
- [ ] A contributor can follow the instructions without access to the maintainer's environment.

## Related work

Preserve the originals privately before deleting their public copies.

## Implementation record, 2026-10-10

This record helps reviewers check the cleanup and locate preserved originals.

- We reviewed all 26 tracked memory files, including metadata and index entries.
- We preserved all originals privately before editing or deleting public copies.
- We checked each archived file against its original bytes and recorded its SHA-256 checksum.
- We retained 18 portable memory files, including the index, and removed eight obsolete records.
- We removed session metadata and replaced environment assumptions with repository commands and document links.
- [docs/archive.rst](../archive.rst), "Removed", records the deleted paths and their source commit.

The private deployment repository stores originals under `.local/contributor-memory-originals/<source-revision>/`.
Its `manifest.json` records the source revision and checksums.
The preserved revision is `04255a1d834360554e02fed4c971d1c9be6181e9`.
These local records stay outside Git.
The maintainer owns their private backup and any later public history cleanup.
The cleanup changes current files, so earlier Git history still contains the original records.

## Validation, 2026-10-10

- All 37 relative links in the 18 retained memory files resolve.
- The index lists every retained note, and all named document headings exist.
- The retained files contain no session metadata, local checkout paths, host capacity, or sandbox instructions.
- All 26 private originals match their Git source bytes and recorded SHA-256 checksums.
- `git diff --check` passed.
- `dev/kasvimuseo docs --clean` passed and reported the generated `index.html`.

The change affects contributor documentation only.
Application behavior stays unchanged.
User acceptance remains pending.
