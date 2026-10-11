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

## Implementation status, 2026-10-10

The maintainer must confirm the project license, copyright holder, and any contributor constraints.
The repository and available commit subjects record no project license choice.
Implementation and artifact checks wait for that decision.

## Decision and validation, 2026-10-11

The maintainer selected the project terms and copyright holder recorded in [LICENSE](../../LICENSE).
The maintainer specified no additional contributor constraints.
The [SPDX license entry](https://spdx.org/licenses/BSD-3-Clause.html) supplies the identifier and standard text.
The copyright years cover the repository history, which starts in 2011.
This decision resolves the blocker recorded on 2026-10-10.

- The container artifact suite passed all 13 tests.
- The source distribution and wheel contain the exact project license text and matching metadata.
- The release checker rejects a wheel with the project license removed.
- The production image built successfully and contains the exact project license text and matching metadata.
- The clean documentation build passed.

Run the artifact suite with `dev/kasvimuseo app test kasvimuseo/tests/test_release_artifacts.py -q`.
The completion checks remain unchecked until the maintainer accepts the work.
