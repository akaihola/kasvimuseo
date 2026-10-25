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

## Completion record, 2026-10-25

Both suites now run on the agents' NixOS host. The changes touch `README.rst` and `dev/kasvimuseo` only.

### What changed

- For the person who uses the site: nothing.
- For the person who works on it: on NixOS, run each suite in `nix-shell -p postgresql`. The helper names a missing PostgreSQL tool, and it names a socket path that is too long. `app browser-test` gives pytest the nix-ld libraries by itself.
- `dev/kasvimuseo`: the new `require_postgres` runs at the start of `db_start`. It stops with a message when `initdb`, `pg_ctl` or `psql` is not on `PATH`, or when the socket path is over 107 bytes.
- `dev/kasvimuseo`, `browser_test`: when `NIX_LD_LIBRARY_PATH` is set, pytest and the browsers get it as `LD_LIBRARY_PATH`. The seed command runs podman, so it gets `env -u LD_LIBRARY_PATH`. Without `NIX_LD_LIBRARY_PATH`, as in CI, nothing changes.
- `README.rst`, "Testing": a new "On NixOS" paragraph with the two commands.

### Findings

- PostgreSQL allows a Unix socket path of 107 bytes. A T3 task worktree path makes `.dev/run/.s.PGSQL.5432` 142 bytes long, and `pg_ctl` then said only "could not start server". We ran every suite from a detached worktree with a short path under the sandbox's temporary directory.
- Without the nix-ld libraries, uv's Python failed with `ImportError: libstdc++.so.6` when it imported greenlet.
- WebKit, run once with `KASVIMUSEO_BROWSER_ENGINES=webkit`: 7 failed and 36 errors out of 43. All 43 stopped with `TargetClosedError` at `BrowserContext.new_page`. A probe with `DEBUG=pw:browser` showed the cause: `Could not create EGL display: no supported platform available. Aborting...`. This is the host environment (no GL driver), not this issue. The receipt therefore records the Chromium run only.
- PostgreSQL from Nix was 18.6. The image tag was `kasvimuseo-dev-task21`.

### Checks before the merge

On the task branch, before the rebase (same content as the delivery commits):

- `nix-shell -p postgresql --run 'dev/kasvimuseo app test'`: 605 passed, 1 xfailed.
- `KASVIMUSEO_BROWSER_ENGINES=chromium nix-shell -p postgresql --run 'dev/kasvimuseo app browser-test'`: 43 passed.
- `KASVIMUSEO_BROWSER_ENGINES=webkit ...`: the EGL failures above.
- `dev/kasvimuseo docs --clean`: exit 0, no warnings. The README is included in the docs.
- Without the PostgreSQL tools, `dev/kasvimuseo app test` stopped with the new message about `initdb`. From the long worktree path, it stopped with the new socket path message.

### Checks at the merged commit

The receipt is [21-make-the-app-and-browser-suites-run-on-nixos-with-postgresql-tools-fro.evidence.json](21-make-the-app-and-browser-suites-run-on-nixos-with-postgresql-tools-fro.evidence.json). Base `e25beb8`, merged `1e3038f`. All four checks passed:

- `app-test`: the image build, then `dev/kasvimuseo app test` in `nix-shell -p postgresql`: 605 passed, 1 xfailed.
- `browser-test-chromium`: the image build, then `KASVIMUSEO_BROWSER_ENGINES=chromium dev/kasvimuseo app browser-test`: 43 passed.
- `delivery-scope`: the delivery changes only `README.rst` and `dev/kasvimuseo`, in the four listed commits.
- `no-private-paths`: no added line holds a home path, a host name or a T3 path.

### Memory reports

- Image build (`dev/kasvimuseo app build`): started at once after a 0 s wait. Admission 57,154 MiB, final 57,120 MiB. Starting swap 1 MiB, growth 0 MiB. 30 s, exit 0.
- Application suite: started at once after a 0 s wait. Admission 57,153 MiB, final 57,104 MiB. Starting swap 1 MiB, growth 0 MiB. 14 s, exit 0.
- Browser suite, Chromium: started at once after a 0 s wait. Admission 57,211 MiB, final 57,150 MiB. Starting swap 1 MiB, growth 0 MiB. 62 s, exit 0.
- Browser suite, WebKit: started at once after a 0 s wait. Admission 57,131 MiB, final 55,473 MiB. Starting swap 1 MiB, growth 0 MiB. 88 s, exit 1 (the EGL failures).
- Documentation build: started at once after a 0 s wait. Admission 55,998 MiB, final 55,055 MiB. Starting swap 1 MiB, growth 0 MiB. 16 s, exit 0.
- Recording `app-test`: started at once after a 0 s wait. Admission 57,305 MiB, final 55,480 MiB. Starting swap 1 MiB, growth 0 MiB. 14 s, exit 0.
- Recording `browser-test-chromium`: started at once after a 0 s wait. Admission 55,488 MiB, final 56,847 MiB. Starting swap 1 MiB, growth 0 MiB. 58 s, exit 0.
- Recording `delivery-scope`: started at once after a 0 s wait. Admission 56,847 MiB, final 56,866 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 0.
- Recording `no-private-paths`: started at once after a 0 s wait. Admission 56,869 MiB, final 56,887 MiB. Starting swap 1 MiB, growth 0 MiB. 2 s, exit 0.

### Open, for the steward

- Workers on [22], [23] and [24] must run the suites from a checkout with a short path, because their T3 worktree paths are too long for the socket. The README and the helper's message say so.
- `.agents/memory/run-the-suite-in-the-container.md` does not point to the "On NixOS" paragraph yet. This issue's scope allowed only `README.rst` and `dev/kasvimuseo`.
- WebKit cannot run on this host until it has a GL driver.
