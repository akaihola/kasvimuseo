Steward issue, 2026-10-25 18:17 refill (steward decisions D48, D53 and D95). Goal: kasvimuseo is a personal favour (tier 3 in `<steward-vault>/Goals.md`) and a public site. Unlabelled. Estimated 1 h.

Tracker: [the kasvimuseo tracker](../../TASKS.md).

## Why

A vault check of every tracker's `main` on 2026-10-25 found `dev/kasvimuseo app test` not runnable on the agents' NixOS host: Podman is there, but `initdb`, `pg_ctl` and `psql` are not on `PATH`, so neither suite ran. The fixes drafted by [the 2026-10-25 security review](../reviews/2026-10-25-security-review.md) need both suites, and the next three issues depend on this one. The steward checked on 2026-10-25 18:25: rootless Podman 5.8.7 works for the agent account, and `nix-shell -p postgresql` provides PostgreSQL 18.6 with all three tools. CI takes Ubuntu's newest PostgreSQL, so no fixed version is expected.

## Work

1. Run `dev/kasvimuseo app build` and `dev/kasvimuseo app test` with the PostgreSQL tools from Nix, for example `nix-shell -p postgresql --run 'dev/kasvimuseo app test'`. Change `dev/kasvimuseo` only where NixOS needs it, for example a clear message that names a missing tool; keep the test contract CI uses.
2. Run `dev/kasvimuseo app browser-test` with Chromium, then once with WebKit. For Playwright follow `~/.config/coding-agents/playwright.md`: the browsers are pre-installed, never run `playwright install`, and pin the Python package from `$UV_CONSTRAINT`. If the host Python's Playwright can't load `libstdc++.so.6`, use the `LD_LIBRARY_PATH="$NIX_LD_LIBRARY_PATH"` prefix that rollscore documents.
3. Add a short "On NixOS" paragraph to the Testing section of `README.rst` with the commands that worked.

## Acceptance

- `dev/kasvimuseo app test` passes on `main` after the merge (585 tests passed in August).
- `KASVIMUSEO_BROWSER_ENGINES=chromium dev/kasvimuseo app browser-test` passes.
- The changes touch only `README.rst` and, if needed, `dev/kasvimuseo`; the CI workflow, settings, requirements and tests are unchanged.
- The check receipt records the two commands above and a scope check.
- Work in your task worktree or a `$TMPDIR` clone, never in the base checkout: its `.dev`, `media`, `static` and `ylaneenkasvit/local_settings.py` links point into kasvimuseo-deployment's private state. Don't open or follow those links.
- WebKit can't create an EGL display on this host (no GL driver; gogo-dashboard found the same on 2026-10-25). WebKit failures that are EGL start-up aborts (`TargetClosedError` at `new_page`) are host environment, not a failure of this issue: record the browser check in the receipt with `KASVIMUSEO_BROWSER_ENGINES=chromium`, so every recorded check passes, and note the WebKit run's outcome in this file. Any other WebKit failure is recorded with its cause.
- No deployment, push, request to the live site or message to anyone.
- Memory: before each heavy command (an image build, a test suite, a dependency audit), wait up to 10 minutes for `MemAvailable` of at least 2 GiB; if it doesn't come, start the command anyway when at least 1.5 GiB is available. Stop a running command when `MemAvailable` falls below 1 GiB or swap grows by more than 512 MiB.
- Keep private paths and host names out of committed docs and code; the check receipt is exempt.
- Handoff: a short outcome and anything left for the owner; detail goes in this file.
