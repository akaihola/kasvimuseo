---
depends-on: []
---

# 11. Move the browser tests to Playwright 1.63

This task helps contributors run the browser checks again on a development host whose browser builds changed.

- Priority: High.
- Owner: Development tooling maintainer.

## Work

1. Change the `playwright` pin in `browser_tests/requirements.txt` to the release that matches the host's browser builds.
2. Run `dev/kasvimuseo app browser-test` with Chromium and with WebKit.
3. Update `test_a_fitted_name_is_drawn_at_the_size_it_was_fitted_to` in `browser_tests/test_label_editor.py` for the new WebKit result.
4. Record the new WebKit result in issue 062.

## Evidence

The repository pins `playwright~=1.61.0`.
On 2026-10-05 the host's current browser builds matched Playwright 1.63.
The older builds no longer start, because they need an older C library than the host provides.
Every browser check therefore fails at browser launch with the current pin.

With a temporary 1.63 pin, Chromium passed all 36 checks.
WebKit passed 28 checks, skipped 7, and failed 1.
The failing check expects WebKit to draw fitted label text larger than fitted, which is the floor that issue 062 describes.
WebKit build 2359 drew the text at the fitted size, 16 pixels.
The branch from before the rebase fails the same way, so the browser update causes the failure.

Issue 062 is `Rejected`, because the maintainer saw correct titles on the iPad.
Its test stays in the suite to show when the floor moves, and the floor has now moved.

## Completion checks

- [ ] Both engines pass `dev/kasvimuseo app browser-test` on the development host.
- [ ] Continuous integration installs the browser builds that match the new pin.
- [ ] Issue 062 records the WebKit result and the build that changed it.
