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

## Completion record, 2026-10-25

The iframe loader now resizes the frame only for a message from the catalogue frame. The debug mode stays and writes text only.

### What changed

- For the person who uses the site: nothing, when the museum's other site embeds the catalogue as before. A page that posts to the museum's other site can no longer resize the frame, scroll the page or write into it.
- For the person who works on it: the loader rejects a message unless all of these are true:
  - its origin is the catalogue origin, that is, the origin of the frame address;
  - its source is the catalogue frame's window;
  - its height is a string of digits followed by `px`, at most `100000px`.
- The debug box (`?debug=1`) is now an element that the loader creates. Each accepted message adds one line, written with `textContent`.
- The `attachEvent` fallback is gone. The loader already needs `URL` and `document.currentScript`, which no browser with only `attachEvent` has.
- [planted-species-iframe.js](../../kasvimuseo/static/js/kasvimuseo/planted-species-iframe.js): the checks and the debug box.
- [browser_tests/test_iframe_loader.py](../../browser_tests/test_iframe_loader.py): 22 new cases per engine.
  - `test_message_from_another_window_changes_nothing`: four hostile senders, each with and without `?debug=1`. The senders are a frame on another origin, another frame on the catalogue origin, the catalogue frame after a navigation to another origin, and an opener page on another origin.
  - `test_catalogue_frame_sets_the_height`: `1234px` and the limit, `100000px`. The page also scrolls to the frame.
  - `test_catalogue_frame_height_must_be_whole_pixels`: eleven bad heights, with the debug box on.
  - `test_debug_mode_shows_markup_in_a_plant_name_as_text`.
- [README.rst](../../README.rst), "Embedding the species list": a paragraph with the message rule and the debug mode.
- [.agents/memory/iframe-loader-checks.md](../../.agents/memory/iframe-loader-checks.md): the note names the message checks.

### Findings

- The new cases failed against the old loader: 20 of the 22 new cases failed in Chromium. The two cases that passed are the two that the catalogue frame sends with a good height.
- A redirect of the catalogue address to another origin, for example from `http` to `https`, now stops the resize. The README says so.
- WebKit, run once with `KASVIMUSEO_BROWSER_ENGINES=webkit` through the helper: 29 failed and 36 errors out of 65. All 65 stopped with `TargetClosedError` at `BrowserContext.new_page`. This is the EGL start-up abort that [task 21](21-make-the-app-and-browser-suites-run-on-nixos-with-postgresql-tools-fro.md) found, so the receipt records the Chromium run only.
- We ran every suite from a detached worktree with a short path, because the task worktree path is too long for the PostgreSQL socket. The image tag was `kasvimuseo-dev-task23`.

### Checks before the merge

On the task branch at `63f882a`, before the rebase:

- `browser_tests/test_iframe_loader.py` alone, in Chromium, through `uv run` on the host: 29 passed.
- The same module with the old loader and the new tests: 20 failed, 9 passed.
- The same module in WebKit: 29 failed, all with the EGL abort above.
- `KASVIMUSEO_IMAGE=kasvimuseo-dev-task23 nix-shell -p postgresql --run 'dev/kasvimuseo app build'`: exit 0.
- `... dev/kasvimuseo app test`: 605 passed, 1 xfailed.
- `KASVIMUSEO_BROWSER_ENGINES=chromium ... dev/kasvimuseo app browser-test`: 65 passed.
- `KASVIMUSEO_BROWSER_ENGINES=webkit ... dev/kasvimuseo app browser-test`: the EGL failures above.
- `dev/kasvimuseo docs --clean`: exit 0, no warnings.

### Memory reports

- The three single-module runs above took 2 s, 8 s and 39 s. They ran without the guard, after a reading of 57,327 MiB available and 1 MiB of swap.
- Image build: started at once after a 0 s wait. Admission 56,922 MiB, final 56,943 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 0.
- Application suite: started at once after a 0 s wait. Admission 56,942 MiB, final 56,911 MiB. Starting swap 1 MiB, growth 0 MiB. 19 s, exit 0.
- Browser suite, Chromium: started at once after a 0 s wait. Admission 56,911 MiB, final 57,276 MiB. Starting swap 1 MiB, growth 0 MiB. 48 s, exit 0.
- Browser suite, WebKit: started at once after a 0 s wait. Admission 56,883 MiB, final 55,200 MiB. Starting swap 1 MiB, growth 0 MiB. 131 s, exit 1 (the EGL failures).
- Documentation build: started at once after a 0 s wait. Admission 55,970 MiB, final 56,406 MiB. Starting swap 1 MiB, growth 0 MiB. 12 s, exit 0.

### Checks at the merged commit

The receipt is [23-check-the-message-origin-in-the-iframe-loader.evidence.json](23-check-the-message-origin-in-the-iframe-loader.evidence.json). Base `9f47521`, merged `1319cb1`. All five checks passed:

- `app-test`: the image build, then `dev/kasvimuseo app test` in `nix-shell -p postgresql`: 605 passed, 1 xfailed.
- `browser-test-chromium`: the image build, then `KASVIMUSEO_BROWSER_ENGINES=chromium dev/kasvimuseo app browser-test`: 65 passed. They include the 22 new cases for the acceptance conditions.
- `loader-static`: the loader has no `document.write`, `innerHTML` or `attachEvent`, and it has the origin, source and `textContent` lines.
- `delivery-scope`: the delivery changes only the five listed files, in the three listed commits.
- `no-private-paths`: no added line holds a home path, a host name or a T3 path.

### Memory reports for the record calls

- Recording `app-test`: started at once after a 0 s wait. Admission 56,689 MiB, final 56,735 MiB. Starting swap 1 MiB, growth 0 MiB. 14 s, exit 0.
- Recording `browser-test-chromium`: started at once after a 0 s wait. Admission 56,735 MiB, final 56,627 MiB. Starting swap 1 MiB, growth 0 MiB. 54 s, exit 0.
- Recording `loader-static`: started at once after a 0 s wait. Admission 56,627 MiB, final 54,913 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 0.
- Recording `delivery-scope`: started at once after a 0 s wait. Admission 54,893 MiB, final 53,821 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 0.
- Recording `no-private-paths`: started at once after a 0 s wait. Admission 53,818 MiB, final 53,698 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 0.

### Open, for the owner

- The change takes effect on the live site only after a deployment. This issue made no deployment.
- A notice to the operators of the museum's other site is optional (owner decision, 2026-11-02). Nothing was sent.

### The museum's other site needs no change

On 2026-11-02 the owner read the source of the other site's page with the species list. The page loads the loader from the catalogue's static host over `https`. A deployment therefore replaces the script at the address that the page already uses. The frame id, the frame address and the `?debug=1` switch did not change.

The resize keeps working after the deployment on two conditions. Nobody checked them on the live site:

- The catalogue address that the loader derives must answer without a redirect to another origin. Otherwise the loader rejects the catalogue's messages, and the frame stays 10000px tall.
- The species list must stay below 100000px. At about 80px for each row, that is about 1,250 species.

A browser that cached the old script keeps it until its copy expires. The static server's cache headers in the deployment configuration set that time.
