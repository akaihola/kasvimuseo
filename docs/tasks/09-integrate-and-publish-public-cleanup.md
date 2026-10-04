---
depends-on: [1, 2, 3, 4, 5, 6, 7, 8]
---

# 09. Integrate and publish the public cleanup

This proposal helps the maintainer deliver the reviewed cleanup to contributors through the public integration branch.

- Priority: High.
- Proposed owner: Project maintainer.

## Proposed work

1. Locate the prepared cleanup and compare it with current integration changes.
2. Preserve unrelated work when preparing the final changes.
3. Resolve the content, packaging, and documentation proposals in this register.
4. Run the required application checks and a clean documentation build on the final tree.
5. Inspect the release artifacts before publication.
6. Commit, integrate, and publish the accepted cleanup.
7. Check the result through a fresh clone and newly generated documentation.

## Review evidence

The review assessed uncommitted cleanup changes. The supplied review checkout and the public integration branch still contained the earlier tree.
A separate prepared checkout and base checkout also contained different unrelated edits.

## Completion checks

- [ ] A fresh public clone contains the accepted cleanup.
- [ ] Required checks pass against the integrated revision.
- [ ] Published packages and documentation match that revision and pass the content checks.
- [ ] The maintainer records any remaining publication or history work in the appropriate private records.

## Dependencies

Complete proposals 01 through 08 before declaring the public cleanup ready. Coordinate external publication work with the maintainer.
