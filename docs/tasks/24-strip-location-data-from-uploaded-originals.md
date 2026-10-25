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
