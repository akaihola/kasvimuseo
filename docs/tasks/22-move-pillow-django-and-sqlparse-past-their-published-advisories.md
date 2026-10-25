---
depends-on: [21]
---

Steward issue, 2026-10-25 18:17 refill (steward decisions D48, D53 and D95). Goal: kasvimuseo is a personal favour (tier 3 in `<steward-vault>/Goals.md`) and a public site. Labelled `security` (steward decision D68). Estimated 1.5 h.

Tracker: [the kasvimuseo tracker](../../TASKS.md).

## Why

Draft K1 of [the 2026-10-25 security review](../reviews/2026-10-25-security-review.md#k1-move-the-locks-past-the-published-advisories), its first "do this first" (findings 1 and 11). `requirements/production.txt` pins Pillow 12.3.0, which has 41 published advisories fixed in 13.0.0, many of them memory-safety bugs in the image decoders that run on every staff upload.

## Work

1. Check that photologue 3.20 works with Pillow 13: its upload, resizing and effects. Issue 028 records the last Pillow break.
2. Set Pillow to 13.0.0 or later in `requirements/production.in`, Django to 6.0.8 or later and sqlparse to 0.6.0 or later. Set Werkzeug to 3.1.9 or later in the development lock and pytest to 9.0.3 or later in the testing lock. Record a reason for any package that can't move.
3. Regenerate the three locks the way issue 027 records, and refresh `docs/dependency-inventory.rst` with `dev/deps-inventory`.

## Acceptance

- pip-audit reports no advisory for the three locks, or this file names each remaining advisory with its reason. If pip-audit can't write its cache in the sandbox, give it `--cache-dir "$TMPDIR/pip-audit"` and run uvx as `UV_TOOL_DIR=$TMPDIR/uvtools uvx pip-audit …`.
- `dev/kasvimuseo app test` and the Chromium browser suite pass on `main` after the merge.
- Deploying is out of scope: the review's KD1 is the owner's step in kasvimuseo-deployment. Name it in the handoff.

## Checks

- `uvx pip-audit -r requirements/production.txt --no-deps --disable-pip`, and the same for `requirements/dev.txt` and `requirements/testing.txt`.
- `dev/kasvimuseo app test` and `KASVIMUSEO_BROWSER_ENGINES=chromium dev/kasvimuseo app browser-test`, run the way the issue this one depends on documents.

## Constraints
- Work in your task worktree or a `$TMPDIR` clone, never in the base checkout: its `.dev`, `media`, `static` and `ylaneenkasvit/local_settings.py` links point into kasvimuseo-deployment's private state. Don't open or follow those links.
- WebKit can't create an EGL display on this host (no GL driver; gogo-dashboard found the same on 2026-10-25). WebKit failures that are EGL start-up aborts (`TargetClosedError` at `new_page`) are host environment, not a failure of this issue: record the browser check in the receipt with `KASVIMUSEO_BROWSER_ENGINES=chromium`, so every recorded check passes, and note the WebKit run's outcome in this file. Any other WebKit failure is recorded with its cause.
- No deployment, push, request to the live site or message to anyone.
- Memory: before each heavy command (an image build, a test suite, a dependency audit), wait up to 10 minutes for `MemAvailable` of at least 2 GiB; if it doesn't come, start the command anyway when at least 1.5 GiB is available. Stop a running command when `MemAvailable` falls below 1 GiB or swap grows by more than 512 MiB.
- Keep private paths and host names out of committed docs and code; the check receipt is exempt.
- Handoff: a short outcome and anything left for the owner; detail goes in this file.

## Completion record, 2026-10-25

The three locks now hold no package with a published advisory. Deploying is the owner's step KD1 in kasvimuseo-deployment.

### What changed

- For the person who uses the site: nothing yet. The site gets the new packages when the owner deploys them (KD1).
- For the person who works on it: the development image has Django 6.0.9, Pillow 13.0.0, sqlparse 0.6.0, Werkzeug 3.1.9 and pytest 9.0.3. pytest 9 brings pygments 2.21.0 into the testing lock.
- `requirements/production.in`: Django 6.0.9, Pillow 13.0.0, and a new floor `sqlparse>=0.6.0` with a comment. Django itself asks only for 0.5.0, and `pip-compile` keeps an old pin that its input still allows.
- `requirements/dev.in`: Werkzeug 3.1.9. `requirements/testing.in` and `setup.py`, `tests_require`: pytest 9.0.3.
- `requirements/production.txt`, `requirements/dev.txt`, `requirements/testing.txt`: regenerated. No other pin moved.
- `docs/dependency-inventory.rst`: the release bands, regenerated with `dev/deps-inventory`.
- `.agents/memory/regenerate-the-locks-in-the-resolver-image.md`: a new note that points to the lock recipe in issue 086.

### Version choices

- Django 6.0.9 is the newest 6.0 release. Photologue 3.20 requires `Django<6.1`, so Django 6.1 cannot come in yet.
- pytest 9.0.3 is the release that fixes the advisories, and the newest 9.0 release. pytest-django 4.11.1 stays: it allows pytest 7 and later, and the suite passes with it.
- Every package that the issue named moved. No package needed a reason to stay.

### Photologue 3.20 with Pillow 13

We ran photologue 3.20's own test suite (84 tests, from its sdist) against Django 6.0.9 and sqlparse 0.6.0, once with Pillow 13.0.0 and once with Pillow 12.3.0. The suite covers the zip upload in the admin, the resize and crop, the effects, the reflection, the watermark and the EXIF rotation. We used minimal settings with SQLite, the admin URLs and a demo `base.html`.

- Pillow 13.0.0: 82 passed, 1 skipped, 1 error. Pillow 12.3.0: the same 84 results, test by test.
- The error is `test_releaser_hooks`, which imports the release tool `zest.releaser`. That is not runtime code. Upstream skips the other test because the sdist leaves out its file.
- The run printed no Pillow deprecation warning.
- A probe found every Pillow name that photologue and `kasvimuseo/models.py` use: the transpose constants, `Image.Resampling.LANCZOS`, `ImageFile.MAXBLOCK`, the built-in filters, `ExifTags.IFD`, `ExifTags.Base` and `ImageOps.exif_transpose`.
- The application suite covers the upload path, the orientation fix and both resize branches (issue 028).

### Findings

- On a NixOS host, Python from Nix cannot import Pillow 13.0.0 alone: `ImportError: libz.so.1`. Pillow 12.3.0 imports there. Both wheels need the system `libz.so.1`; after `import zlib` both import. This affects only that host Python, not the images, because their Alpine and Debian bases have zlib.
- sqlparse 0.6.0 rewrites statement splitting, which Django uses for SQL scripts. The application suite passes with it.
- `browser_tests/requirements.txt` allows `pytest~=8.4`. That file is not one of the three locks, so this issue leaves it. A pytest 8 release there carries the advisories that pytest 9.0.3 fixes.
- The research runner could not read the Pillow 13.0.0 release notes. We tried the published page twice and the source file once, and the runner rejected the reader's answer each time. The photologue suite and the probe above stand in for the notes.
- The 10 warnings in `kasvimuseo/tests/test_photo_orientation.py` (a naive `date_taken`) are not new. The task 21 image, with the old packages, gives the same 10.

### Audit results

pip-audit 2.10.1 with `--no-deps --disable-pip`, on each lock:

| Lock | Before | After, PyPI service | After, OSV service |
| --- | --- | --- | --- |
| `requirements/production.txt` | 49 in all: Django 6.0.7 (3), Pillow 12.3.0 (37), sqlparse 0.5.5 (9) | none | none |
| `requirements/dev.txt` | the same 49, and Werkzeug 3.0.6 (7) | none | none |
| `requirements/testing.txt` | pytest 8.3.5 (2) | none | none |

The review counted 41 advisories for Pillow. The PyPI service gave 37 today. No advisory remains, so this file names none.

### Checks before the merge

We ran these on the task branch before the rebase, which changed only `TASKS.md`. We used a detached worktree with a short path and the image tag `kasvimuseo-dev-task22`:

- The resolver image: `python:3.13.16-alpine3.24`, the build packages of `dev/Containerfile`, pip 24.0, setuptools 75.8.0, wheel 0.45.1, pip-tools 7.4.1 and Click 8.1.8. Issue 086, "Lock generation", has the recipe. We ran `pip-compile` with each lock's header options, in the order production, dev, testing.
- `dev/kasvimuseo app build`: exit 0. `pip check` finds no broken requirement. The 19 packages of the dev and testing locks are in the image at their locked versions. The image adds only pip, setuptools and wheel.
- `nix-shell -p postgresql --run 'dev/kasvimuseo app test'`: 605 passed, 1 xfailed. Task 21 had the same count.
- `KASVIMUSEO_BROWSER_ENGINES=chromium nix-shell -p postgresql --run 'dev/kasvimuseo app browser-test'`: 43 passed.
- The same with `KASVIMUSEO_BROWSER_ENGINES=webkit`: 7 failed and 36 errors out of 43. All 43 stop with `TargetClosedError` at `BrowserContext.new_page`, the EGL start-up abort of the host (task 21). The receipt records the Chromium run only.
- `nix-shell -p postgresql --run 'dev/kasvimuseo app coverage'`: exit 0, total 98.85%.
- `dev/kasvimuseo docs --clean`: exit 0, no warnings, and the build wrote the index.
- `dev/deps-inventory`: exit 0. It rewrote the bands of 21 packages, and the header now says 522 bands.

### Memory reports

Every heavy command started at once after a 0 s wait. Starting swap was 1 MiB for each, and swap growth was 0 MiB for each.

| Command | Admission MiB | Final MiB | Time | Exit |
| --- | --- | --- | --- | --- |
| pip-audit before, three locks | 56,784 | 56,712 | 2 s each | 1 each (advisories found) |
| Photologue tests, minimal harness, Pillow 13.0.0 and 12.3.0 | 56,614 | 56,575 | 8 s each | 1 each (harness gaps) |
| Photologue tests with admin URLs, Pillow 13.0.0 and 12.3.0 | 56,739 | 56,758 | 6 s and 7 s | 1 each (the release-tool test) |
| Resolver image build | 56,299 | 56,281 | 6 s | 0 |
| Lock regeneration, three `pip-compile` runs | 56,237 | 56,342 | 6 s | 0 |
| pip-audit after, PyPI service, three locks | 56,469 | 56,318 | 2 s each | 0 each |
| pip-audit after, OSV service, three locks | 56,318 | 56,392 | 4 s each | 0 each |
| `dev/deps-inventory` | 56,211 | 56,121 | 81 s | 0 |
| `dev/kasvimuseo app build` | 56,831 | 56,765 | 10 s | 0 |
| Application suite | 56,850 | 56,753 | 14 s | 0 |
| Browser suite, Chromium | 56,885 | 56,779 | 49 s | 0 |
| Browser suite, WebKit | 56,884 | 54,600 | 90 s | 1 (EGL) |
| Coverage gate | 56,750 | 57,368 | 18 s | 0 |
| Documentation build | 57,452 | 57,450 | 12 s | 0 |
| Orientation tests on the task 21 image | 57,450 | 57,464 | 4 s | 0 |

For a row with more than one run, the admission value is the first run's and the final value is the last run's.

### Open

- The owner: deploy the new locks to production. That is step KD1 of the security review, in kasvimuseo-deployment. Until then, production still decodes uploads with Pillow 12.3.0.
- The steward: `browser_tests/requirements.txt` allows pytest 8.4, which has the advisories that pytest 9.0.3 fixes. A weekly audit (review draft K8) can cover that file too.
- The steward: Django 6.1 waits for a photologue release that allows it.
