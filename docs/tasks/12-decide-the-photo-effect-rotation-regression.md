---
depends-on: [10]
---

# 12. Decide how to handle the rotation regression in photo effects

This task helps the maintainer choose how the project handles a photologue 3.20 regression.

- Priority: Low.
- Owner: Project maintainer.

## Work

1. Read `docs/issues/089-a-photo-effect-leaves-a-phone-photo-sideways.rst`, "Options".
2. Record the decision in the issue's `:Decision:` field.
3. If the decision includes an upstream report, the maintainer sends it from the maintainer's own account.
4. Carry out the chosen option, or set the status that the decision gives.

## Evidence

Photologue 3.20 applies a photo effect before it reads the EXIF orientation, and the effect removes that data.
Photologue therefore caches a phone photo with an effect sideways.
The production dump of 2026-08-26 has no photo effects, so nothing triggers the regression today.
Issue 089 is on the branch that task 10 merges.

## Completion checks

- [ ] Issue 089 records a decision and a status that matches it.
- [ ] `kasvimuseo/tests/test_photo_orientation.py` agrees with the decision.
