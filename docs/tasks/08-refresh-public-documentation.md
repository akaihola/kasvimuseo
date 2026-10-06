---
depends-on: [2, 3, 5, 6, 7, 10]
---

# 08. Refresh public documentation after the repository split

This proposal helps contributors find accurate runtime instructions and public project records after the repository split.

- Priority: Medium.
- Proposed owner: Documentation maintainer.

## Proposed work

1. Update runtime descriptions to match the checked-out code and dependency locks.
2. Remove promises of instructions that the public repository no longer provides.
3. Remove or replace deployment-only issue stubs while preserving valid issue relationships.
4. Remove archive pointers that direct readers to private operational content.
5. Repair commit references and documentation checks after any coordinated history replacement.
6. Rebuild documentation from an empty output directory.

## Review evidence

The prepared [README](../../README.rst) still describes Python 2.7.
[docs/index.rst](../index.rst) promises removed Ansible instructions.
The prepared issue register retains ten deployment-only stubs, and [docs/archive.rst](../archive.rst) points to the earlier operational README.

## Completion checks

- [ ] Documentation describes the current runtime and an independent contributor workflow.
- [ ] Issue rankings, relationships, and remaining archive references are valid.
- [ ] A clean documentation build passes with warnings treated as errors.
- [ ] Generated output contains no removed operational pages.

## Dependencies

Use the final content from proposals 02, 03, 05, 06, and 07. Coordinate commit-reference changes with the maintainer.

Update of 2026-10-06: task 10 lands the Django 6.0 runtime that this documentation must describe.
`docs/issues/next.rst`, "Refill this queue before it empties", still sends readers to `AGENTS.md` for the backlog refill rule.
`docs/issues/incoming.rst` still says that `AGENTS.md` states the rule for incoming reports.
`AGENTS.md` no longer holds either rule.
Step 5 waits for private task 4, which replaces public history. If task 4 has not run when this task ends, task 9 repairs the commit references.
