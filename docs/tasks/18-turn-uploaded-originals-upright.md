---
depends-on: []
---

# 18. Turn uploaded originals upright before photologue stores them

This task helps the contributor who implements option 3 of issue 089 make every stored photo upright, whatever photologue does with the EXIF tag.

- Priority: Medium.
- Owner: Any contributor with the application suite.

## Work

1. Read `docs/issues/089-a-photo-effect-leaves-a-phone-photo-sideways.rst`, "Options" and "Decision".
2. Add a `pre_save` receiver for `Photo` in `kasvimuseo/models.py`, next to `autoconnect_photo_to_species`. It runs only when the image changed.
3. In the receiver, open the upload with Pillow and call `ImageOps.exif_transpose`. Save the result back into the field only when the tag was not 1. Pass the transposed EXIF bytes to the save, and use `quality='keep'` for a JPEG.
4. Write the tests listed under "Completion checks" in `kasvimuseo/tests/test_photo_orientation.py`.
5. Mark the test that bypasses the receiver with `pytest.mark.xfail(strict=True)` and the reason `upstream issue 233`. The strict mark fails the suite when a photologue release fixes the order, which is the signal for task 19.
6. Update the `Evidence` field of issue 089 to name the new tests. Set its `Status` to `Fixed` and name the commit in `Resolution`.

## Evidence

Photologue 3.20 applies a photo effect before it reads the EXIF orientation, and the effect removes that data.
A stored original without an orientation tag needs no transposing, so the work-around holds before and after the upstream fix.
`measure_photo_orientation` in `kasvimuseo/models.py` compares the stored pixel width and height, so a tagged portrait photo gets a landscape label layout today.
Pull request 232 of photologue shows that 3.20 also mishandles orientations 2, 4, 5 and 7. Pillow handles all eight.
Photologue reads `DateTimeOriginal` from the stored file after the save, so the EXIF data must survive the transpose.

## Completion checks

- [ ] A sideways JPEG upload is stored as 20x40 pixels with no orientation tag, and `photo_is_horizontal` is false for its species.
- [ ] The stored file keeps `DateTimeOriginal`, so `date_taken` is set.
- [ ] A PNG and a JPEG with orientation 1 are stored byte for byte as uploaded.
- [ ] The display size of a sideways upload is 20x40 with no effect, with an effect on the photo, and with an effect on the photo size.
- [ ] A test that saves the original without the receiver and gives the photo an effect expects 20x40 and is a strict expected failure.
- [ ] The suite passes on photologue 3.20 with the strict expected failure in place.
- [ ] Issue 089 is `Fixed`.

## Related work

[Task 19](19-remove-the-orientation-work-around.md) proposes to remove the receiver after the upstream fix.
Existing originals keep their tags. A one-off command for them is outside this task and needs its own decision.
