---
depends-on: [21]
---

Steward issue, 2026-10-25 18:17 refill (steward decisions D48, D53 and D95). Goal: kasvimuseo is a personal favour (tier 3 in `<steward-vault>/Goals.md`) and a public site. Labelled `security` (steward decision D68). Estimated 1 h.

Tracker: [the kasvimuseo tracker](../../TASKS.md).

## Why

Draft K2 of [the 2026-10-25 security review](../reviews/2026-10-25-security-review.md#k2-check-the-message-origin-in-the-iframe-loader) (finding 2, the highest-scoring finding). The iframe loader accepts messages from any window, and its debug mode writes message data as HTML. Any visitor of the museum's other site, which embeds the catalogue, can meet it.

## Work

1. In `planted-species-iframe.js`, ignore a message unless its origin is the catalogue's origin and its source is the frame's window.
2. Keep the debug mode, but write its text with `textContent` instead of `document.write`.
3. Accept a height only as digits followed by `px`, with an upper limit.

## Acceptance

- A message from another window changes neither the frame height nor the page, with or without the debug query.
- A message from the catalogue frame still sets the height.
- Markup in a plant name shows as text.
- Telling the operators of the museum's other site that the script changed is the owner's step: name it in the handoff, send nothing.

## Checks

- New cases in `browser_tests/test_iframe_loader.py`, run with `KASVIMUSEO_BROWSER_ENGINES=chromium dev/kasvimuseo app browser-test`, the way the issue this one depends on documents; `dev/kasvimuseo app test` still passes.

## Constraints
- Work in your task worktree or a `$TMPDIR` clone, never in the base checkout: its `.dev`, `media`, `static` and `ylaneenkasvit/local_settings.py` links point into kasvimuseo-deployment's private state. Don't open or follow those links.
- WebKit can't create an EGL display on this host (no GL driver; gogo-dashboard found the same on 2026-10-25). WebKit failures that are EGL start-up aborts (`TargetClosedError` at `new_page`) are host environment, not a failure of this issue: record the browser check in the receipt with `KASVIMUSEO_BROWSER_ENGINES=chromium`, so every recorded check passes, and note the WebKit run's outcome in this file. Any other WebKit failure is recorded with its cause.
- No deployment, push, request to the live site or message to anyone.
- Memory: before each heavy command (an image build, a test suite, a dependency audit), wait up to 10 minutes for `MemAvailable` of at least 2 GiB; if it doesn't come, start the command anyway when at least 1.5 GiB is available. Stop a running command when `MemAvailable` falls below 1 GiB or swap grows by more than 512 MiB.
- Keep private paths and host names out of committed docs and code; the check receipt is exempt.
- Handoff: a short outcome and anything left for the owner; detail goes in this file.
