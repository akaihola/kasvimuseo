---
depends-on: [18]
---

# 19. Remove the orientation work-around after the photologue fix

This task helps the contributor who bumps photologue past the fix of upstream issue 233 decide whether the receiver of task 18 can go.

- Priority: Low.
- Owner: Any contributor with the application suite.

This is a proposal. The maintainer verifies it when the strict expected failure of task 18 fails.

## Work

1. Confirm that the strict expected failure of task 18 fails on the new photologue version, which means photologue reads the tag before the effect.
2. Check whether `measure_photo_orientation` in `kasvimuseo/models.py` still reads pixel dimensions. If it does, the receiver still fixes the label layout, and this task changes the measurement to read the EXIF tag instead of removing the receiver.
3. Check that the new photologue handles all eight orientation values, which pull request 232 adds.
4. Remove the receiver and its tests, or keep it and record why in issue 089.
5. Record the outcome in issue 089, "Decision".

## Evidence

The receiver of task 18 exists for the regression of upstream issue 233 and for the label layout.
The upstream fix removes the first reason only.

## Completion checks

- [ ] Issue 089 records whether the receiver stays, and why.
- [ ] The suite passes without a strict expected failure for upstream issue 233.
