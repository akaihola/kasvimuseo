---
depends-on: [21, 22]
---

Steward issue, 2026-10-25 18:17 refill (steward decisions D48, D53 and D95). Goal: kasvimuseo is a personal favour (tier 3 in `<steward-vault>/Goals.md`) and a public site. Labelled `security` (steward decision D68). Estimated 1.5 h. After the Pillow move, so its tests run on Pillow 13.

Tracker: [the kasvimuseo tracker](../../TASKS.md).

## Why

Draft K4 of [the 2026-10-25 security review](../reviews/2026-10-25-security-review.md#k4-strip-location-data-from-uploaded-originals) (finding 4 and the receiver gap under "Uploads and image handling"). Stored originals keep their GPS tags, and anonymous visitors can download them.

## Work

1. In `turn_photo_upright` (`kasvimuseo/models.py`), remove the GPS block and the owner and serial-number tags from every new upload, also from one without an orientation tag. Keep `DateTimeOriginal` and the orientation fix.
2. Catch `Image.DecompressionBombError` in the same receiver and give the admin a form error.
3. Add a management command that strips the same tags from stored originals, with a mode that only counts the tagged files.
4. Override photologue's `photo_detail.html` so that it links the display size, not the original, and delete the commented address in `planted-species.html` (line 9).
5. Say in a code comment on the receiver, and in this file, that it now does more than the orientation work-around, so that removing the work-around later keeps the tag removal.

## Acceptance

- An upload with location tags is stored without them, with or without an orientation tag; `DateTimeOriginal` stays.
- No public page names the address of an original.
- The command's counting mode reports the number of tagged originals and changes nothing.
- Running the command on production is out of scope: it is the review's KD1, the owner's step in kasvimuseo-deployment. Name it in the handoff.

## Checks

- New cases in `kasvimuseo/tests/test_photo_orientation.py` and `kasvimuseo/tests/test_templates.py`, run with `dev/kasvimuseo app test`, the way the issue this one depends on documents; the Chromium browser suite still passes.
- `dev/kasvimuseo app manage <command> --count` on a development copy built by the tests, not on any real media.

## Constraints
- Work in your task worktree or a `$TMPDIR` clone, never in the base checkout: its `.dev`, `media`, `static` and `ylaneenkasvit/local_settings.py` links point into kasvimuseo-deployment's private state. Don't open or follow those links.
- WebKit can't create an EGL display on this host (no GL driver; gogo-dashboard found the same on 2026-10-25). WebKit failures that are EGL start-up aborts (`TargetClosedError` at `new_page`) are host environment, not a failure of this issue: record the browser check in the receipt with `KASVIMUSEO_BROWSER_ENGINES=chromium`, so every recorded check passes, and note the WebKit run's outcome in this file. Any other WebKit failure is recorded with its cause.
- No deployment, push, request to the live site or message to anyone.
- Memory: before each heavy command (an image build, a test suite, a dependency audit), wait up to 10 minutes for `MemAvailable` of at least 2 GiB; if it doesn't come, start the command anyway when at least 1.5 GiB is available. Stop a running command when `MemAvailable` falls below 1 GiB or swap grows by more than 512 MiB.
- Keep private paths and host names out of committed docs and code; the check receipt is exempt.
- Handoff: a short outcome and anything left for the owner; detail goes in this file.

## The receiver's two jobs

Since this task, `turn_photo_upright` in `kasvimuseo/models.py` does more than the orientation work-around of [task 18](18-turn-uploaded-originals-upright.md). It also removes the private EXIF tags from every upload, also from an upright one. When [task 19](19-remove-the-orientation-work-around.md) removes the work-around, keep the tag removal. The receiver's docstring and task 19 say the same.

## Completion record, 2026-10-25

New uploads lose their location, owner and serial-number tags. A new command removes them from the stored originals. No public page names the address of an original.

### What changed

- For the person who uses the site: an uploaded photo is stored without its GPS block, `CameraOwnerName`, `BodySerialNumber`, `LensSerialNumber` and `CameraSerialNumber`. `DateTimeOriginal` and the other tags stay. The public photo page links the display size. The species sheets no longer hold the original's address in an HTML comment. An admin upload with too many pixels gets the form error "Kuvassa on liian monta kuvapistettä. Lataa pienempi kuva."
- For the person who works on it:
  - `clean_original` in `kasvimuseo/models.py` returns the cleaned bytes, or `None` when the file needs no change. `remove_private_tags` does the tag removal on an `Image.Exif`. The receiver calls `clean_original`, and it raises a `ValidationError` on the image field for a `DecompressionBombError`.
  - `PhotoImageField` in `kasvimuseo/forms.py` gives the admin the same message, because Django's image field refuses the bomb first, with its generic "not an image" message.
  - `dev/kasvimuseo app manage strip_private_exif --count` counts the stored originals with private tags and changes nothing. Without `--count`, the command removes the tags. It replaces each file in one step, keeps its mode, and turns no photo upright. `--verbosity 2` names each tagged file. It reports a file that it cannot read and goes on.
- Paths:
  - [kasvimuseo/models.py](../../kasvimuseo/models.py): `PRIVATE_TAGS`, `PRIVATE_EXIF_TAGS`, `TOO_MANY_PIXELS`, `remove_private_tags`, `clean_original` and `turn_photo_upright`.
  - [kasvimuseo/forms.py](../../kasvimuseo/forms.py): `PhotoImageField`, used by `PhotoForm`.
  - [kasvimuseo/management/commands/strip_private_exif.py](../../kasvimuseo/management/commands/strip_private_exif.py): the command.
  - [kasvimuseo/templates/photologue/photo_detail.html](../../kasvimuseo/templates/photologue/photo_detail.html): the photo page, with new markup.
  - [planted-species.html](../../kasvimuseo/templates/kasvimuseo/reports/planted-species.html): the commented address is gone.
  - [kasvimuseo/locale/fi/LC_MESSAGES/django.po](../../kasvimuseo/locale/fi/LC_MESSAGES/django.po) and its `.mo`: the Finnish form error.
  - Tests: 16 new cases in [test_photo_orientation.py](../../kasvimuseo/tests/test_photo_orientation.py), 9 in [test_templates.py](../../kasvimuseo/tests/test_templates.py) and 1 in [test_admin_forms.py](../../kasvimuseo/tests/test_admin_forms.py).
  - [Task 19](19-remove-the-orientation-work-around.md), "Work" and "Evidence": keep the tag removal.
  - [docs/third-party-notices.rst](../third-party-notices.rst), "What is not vendored": the photo page copies no upstream markup.
  - [.agents/memory/compile-the-finnish-messages-with-babel.md](../../.agents/memory/compile-the-finnish-messages-with-babel.md): a new project memory.

### Findings

- The address of an original is easy to guess from the address of a derived size: photologue stores `photologue/photos/cache/<name>_display.jpg` beside `photologue/photos/<name>.jpg`. So the hidden links help little. The tag removal on the stored originals is what protects the locations.
- Photologue's derived sizes carry no EXIF data, because Pillow writes EXIF only when the save call passes it.
- A changed JPEG is encoded once again, with its own quantization tables and subsampling. Before this task, only a sideways upload was encoded again; now every upload with a private tag is. The receiver now keeps the colour profile, which the orientation fix dropped before.
- A phone photo with a second image, for example a gain map, opens in Pillow as MPO. Before this task, the orientation fix encoded such a file at Pillow's default quality. Now it is stored as a JPEG of its first image, with its own tables.
- The receiver writes only the EXIF block, so an XMP packet in a changed file is dropped. A file that needs no change keeps its XMP packet. If a tool wrote a location only into XMP, that location stays. The camera's `MakerNote` block also stays, and some cameras put a serial number in it. Neither is in this issue's list.
- Pillow raises `DecompressionBombError` above twice `Image.MAX_IMAGE_PIXELS`, that is, above 178,956,970 pixels. Between the limit and twice the limit, Pillow only warns, and the upload goes through as before.
- Copying photologue's `photo_detail.html` would need a license notice in about seven files. The new template uses new markup, so it needs none.
- Babel 2.18.0 made the committed `.mo` file; GNU `msgfmt` gives different bytes. The rebuilt file differs from the old one by the new message only.
- WebKit, run once with `KASVIMUSEO_BROWSER_ENGINES=webkit` through the helper: 29 failed and 36 errors out of 65. All 65 stopped with `TargetClosedError` at `BrowserContext.new_page`. This is the EGL start-up abort that [task 21](21-make-the-app-and-browser-suites-run-on-nixos-with-postgresql-tools-fro.md) found, so the receipt records the Chromium run only.

### Checks before the merge

On the task branch at `9f67a9d`, before the rebase, from a detached worktree with a short path. The image tag was `kasvimuseo-dev-task24`.

- `nix-shell -p postgresql --run 'dev/kasvimuseo app build'`: exit 0.
- `... dev/kasvimuseo app test`: 631 passed, 1 xfailed. Before this task, the suite had 605 tests.
- `KASVIMUSEO_BROWSER_ENGINES=chromium ... dev/kasvimuseo app browser-test`: 65 passed.
- The command on a development copy: a fresh database from the migrations, with two originals that the tests' own `save_photo` and `tagged_image_bytes` stored with the receiver off. `strip_private_exif --count` printed "1 of 2 originals have private tags." and changed no file. Then `strip_private_exif` printed "Removed the private tags from 1 of 2 originals.", and `--count` printed "0 of 2 originals have private tags.". No real media was involved.
- `KASVIMUSEO_BROWSER_ENGINES=webkit ... dev/kasvimuseo app browser-test`: the EGL failures above.
- `dev/kasvimuseo docs --clean`: exit 0, no warnings.
- The first run of the command check stopped at once: `psql` read the relative socket directory `.dev/run` as a host name. The second run used an absolute path and passed.

### Memory reports

- Image build: started at once after a 0 s wait. Admission 56,763 MiB, final 56,607 MiB. Starting swap 1 MiB, growth 0 MiB. 6 s, exit 0.
- Application suite: started at once after a 0 s wait. Admission 56,606 MiB, final 56,681 MiB. Starting swap 1 MiB, growth 0 MiB. 14 s, exit 0.
- Browser suite, Chromium: started at once after a 0 s wait. Admission 56,758 MiB, final 56,514 MiB. Starting swap 1 MiB, growth 0 MiB. 54 s, exit 0.
- Command check on a development copy, first run: started at once after a 0 s wait. Admission 56,681 MiB, final 56,691 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 2 (the socket path above).
- Command check on a development copy, second run: started at once after a 0 s wait. Admission 56,708 MiB, final 56,620 MiB. Starting swap 1 MiB, growth 0 MiB. 6 s, exit 0.
- Browser suite, WebKit: started at once after a 0 s wait. Admission 56,653 MiB, final 55,613 MiB. Starting swap 1 MiB, growth 0 MiB. 120 s, exit 1 (the EGL failures).
- Documentation build: started at once after a 0 s wait. Admission 56,428 MiB, final 56,468 MiB. Starting swap 1 MiB, growth 0 MiB. 12 s, exit 0.

### Open, for the owner

- Run the command on production. This is the review's KD1, the owner's step in kasvimuseo-deployment. Deploy this change first, so that no new upload adds tags. Then run `strip_private_exif --count`, and then `strip_private_exif` if the count is not zero. A positive count means that the exposure was real. Keep a backup of the originals before the second command.
- The change takes effect on the live site only after a deployment. This issue made no deployment.

### Checks at the merged commit

The receipt is [24-strip-location-data-from-uploaded-originals.evidence.json](24-strip-location-data-from-uploaded-originals.evidence.json). Base `7f17822`, merged `bf07e54`. All six checks passed:

- `app-test`: the image build, then `dev/kasvimuseo app test` in `nix-shell -p postgresql`: 631 passed, 1 xfailed. They include the new cases for the first two acceptance conditions.
- `browser-test-chromium`: the image build, then `KASVIMUSEO_BROWSER_ENGINES=chromium dev/kasvimuseo app browser-test`: 65 passed.
- `strip-command-on-a-development-copy`: the command check from "Checks before the merge", on a fresh database and an empty media directory in the clean checkout. `--count` printed "1 of 2 originals have private tags." and changed no file. The strip run printed "Removed the private tags from 1 of 2 originals.", and `--count` then printed "0 of 2 originals have private tags.".
- `no-original-address`: no template under `kasvimuseo/templates/kasvimuseo` or `kasvimuseo/templates/photologue` uses `image.url`, and the photo page links `get_display_url`.
- `delivery-scope`: the delivery changes only the 17 listed files, in the three listed commits.
- `no-private-paths`: no added line holds a home path, a host name or a T3 path.

### Memory reports for the record calls

- Recording `app-test`: started at once after a 0 s wait. Admission 56,931 MiB, final 56,839 MiB. Starting swap 1 MiB, growth 0 MiB. 14 s, exit 0.
- Recording `browser-test-chromium`: started at once after a 0 s wait. Admission 56,840 MiB, final 56,907 MiB. Starting swap 1 MiB, growth 0 MiB. 51 s, exit 0.
- Recording `strip-command-on-a-development-copy`: started at once after a 0 s wait. Admission 56,909 MiB, final 56,794 MiB. Starting swap 1 MiB, growth 0 MiB. 6 s, exit 0.
- Recording `no-original-address`: started at once after a 0 s wait. Admission 56,795 MiB, final 56,826 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 0.
- Recording `delivery-scope`: started at once after a 0 s wait. Admission 56,826 MiB, final 56,873 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 0.
- Recording `no-private-paths`: started at once after a 0 s wait. Admission 56,875 MiB, final 56,906 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 0.
