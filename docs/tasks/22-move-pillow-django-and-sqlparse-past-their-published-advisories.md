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
