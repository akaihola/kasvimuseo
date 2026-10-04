---
depends-on: []
---

# 06. Declare the project license

This proposal helps the maintainer state the terms under which contributors and users can reuse the project.

- Priority: High.
- Proposed owner: Project maintainer.

## Proposed work

1. Confirm the maintainer's chosen license and any contributor constraints.
2. Add the license text at the repository root.
3. Declare the license in package metadata and link it from the README.
4. Check that distributed application artifacts include the license.

## Review evidence

The prepared public tree has no project LICENSE, COPYING, or equivalent file.
[setup.py](../../setup.py) declares no project license.

## Completion checks

- [ ] The repository names a specific license and includes its text.
- [ ] The README and package metadata agree with that choice.
- [ ] Built source and wheel artifacts contain the applicable project license.

## Related work

Review third-party obligations separately in [proposal 07](07-preserve-vendored-license-notices.md).
