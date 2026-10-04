---
depends-on: []
---

# 02. Keep contributor memories portable

This proposal helps contributors retain reusable project knowledge while removing machine-specific records from public documentation.

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
