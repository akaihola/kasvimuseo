Steward issue, 2026-10-25 16:19 refill (steward decisions D48 and D53: Claude's week resets within a day with 44 % unused). Goal: kasvimuseo is a personal favour (tier 3 in `<steward-vault>/Goals.md`), and it is a public site, so a breach would hurt someone else. Labelled `security` (security work stays on Claude, steward decision D68). Estimated 1.5 h.

## Why

The kasvimuseo Django app has never had a security review. kasvimuseo-deployment's [2026-10-21 security review](http://tinni/prg/kasvimuseo-deployment/docs/reviews/2026-10-21-security-review.md?f) covered the playbooks, credentials and site settings. It drafted three findings that belong in this repository, among them the password-free development login (`ylaneenkasvit/dev_login.py`, `KASVIMUSEO_DEV_LOGIN` read with `bool(os.environ.get(...))` in `ylaneenkasvit/common_settings.py`, and `dev/kasvimuseo` defaults). None is filed in this tracker. The app code (views, forms, uploads, templates, admin, the dashboard) was outside that review.

## Work

1. Use the `security-review` skill over the tree: `ylaneenkasvit/`, `kasvimuseo/`, `jqm/`, `dev/`, `browser_tests/` (as evidence of intended behaviour), `Dockerfile`, `setup.py` and `requirements/`. Skip the `media` and `static` links: they point into another repository's local data. Cover at least:
   - authentication and the development login: how it is switched on, whether production can reach it, and what it grants;
   - authorization: which views change data, and what guards each (admin, dashboard, editing, uploads);
   - uploads and image handling: photologue, accepted types and sizes, decompression bombs, EXIF handling (issue [18]'s code), and where files land and are served from;
   - templates: `|safe`, `mark_safe`, `format_html` misuse, and user text reaching JavaScript;
   - CSRF exemptions, raw SQL, open redirects, and error pages that leak detail;
   - settings that reach production: `DEBUG`, `SECRET_KEY` source, `ALLOWED_HOSTS`, cookie and HTTPS flags, and how `common_settings.py`, `settings.py` and `local_settings.py` combine;
   - pinned dependency versions in `requirements/` and `docs/requirements.txt` against known advisories. Use `uvx pip-audit` if it reaches its advisory source; otherwise list the versions with the reason.
2. Recheck the three kasvimuseo findings from the deployment review on current `main`: say which still hold, and don't draft duplicates. Read `docs/issues/` too (for example issues 025 and 026) so the report doesn't re-report fixed items.
3. Search the history for secrets (`git log -p`), and check ignored and untracked files by name only. Name the file and commit, never the value.
4. Write the report to `docs/reviews/2026-10-25-security-review.md`, next to `docs/tasks/`. Rank the findings by impact and likelihood, each with file and line evidence. End with `## Do these first` and a `## Draft issues` section: one draft per fix worth making (title, work, acceptance, checks). Say which drafts belong in kasvimuseo-deployment instead. Link paths as relative links. Don't fix anything in this issue, and don't file the drafts.
5. A live credential in the tree, the history or an ignored file is urgent: say so first in your completion message, with its location only.

## Acceptance

- The report exists, covers every area in step 1 or says why one was skipped, rechecks the three earlier findings, and drafts an issue for each finding worth fixing.
- No secret value appears in the report, the commit or the thread.
- Read-only: no code change, no request to the live site, no deployment, push or service start. Don't open credential files or the `media` and `static` targets; the code tells you how they are used. Running the app's test suite is optional; don't install or start a database for it.
- Memory: before each heavy command (a scan over the whole history, a dependency audit), wait up to 10 minutes for `MemAvailable` of at least 2 GiB; if it doesn't come, start the command anyway when at least 1.5 GiB is available. Stop a running command when `MemAvailable` falls below 1 GiB or swap grows by more than 512 MiB.
- Keep private paths out of committed docs and code; the check receipt is exempt.
- Handoff: a short outcome (first line: any live credential, or "no live credential found") and the report's top findings; detail goes in the report and this task record.

Tracker: [the kasvimuseo tracker](../../TASKS.md).

## Progress record, 2026-10-25

This record is for the steward and for the agent that finishes this task. The review is not complete.

### Safeguard stop

A provider safety classifier stopped one response of the review session. The response was about the third-party grappelli views (the related lookups and the user switch). We did not retry that material, and we did not review those views.

### Acceptance conditions that are not met

- The report `docs/reviews/2026-10-25-security-review.md` does not exist.
- Therefore the area coverage, the ranked findings, `## Do these first` and `## Draft issues` are not written.
- The handoff of the top findings is not given.
- The false-positive check of the `security-review` skill did not run on the candidates below.

These conditions are met so far: no code change, no request to the live site, no deployment, no push and no service start. No secret value is in this file, in the commit or in the thread. The scans printed rule names, paths, commit ids and value shapes only.

### Work done before the stop

- History scan: a script read every blob of every reference, and the unreachable objects (2,324 blobs, 1,430 commit messages). It found no live credential. The matches are test fixtures, development defaults and the `***REMOVED***` markers of the history rewrite.
- Ignored files, by name only: the `.dev`, `media`, `static` and `ylaneenkasvit/local_settings.py` links of the base checkout point into the ignored state of kasvimuseo-deployment. Its 2026-10-21 review lists that state. Five old agent task worktrees outside this repository keep `.dev/docs/` build output from before the history rewrite. Its page titles name the credentials that production rotated on 2026-08-26. We did not open these files.
- Recheck of the deployment review's kasvimuseo findings on `main`:
  - A1 still holds: [common_settings.py](../../ylaneenkasvit/common_settings.py) lines 283 and 285 use `bool(os.environ.get(...))`, and [dev/kasvimuseo](../../dev/kasvimuseo) line 40 turns `DEV_LOGIN` on by default.
  - A2 still holds: `MIDDLEWARE` (lines 92-99) has no `SecurityMiddleware`, and no settings module sets `AUTH_PASSWORD_VALIDATORS`.
  - A3 still holds: on 2026-10-25, `git ls-remote` showed `fix-ipad-label-font-size` at `1cc5996` and `feature/fix-issue-018-run-th-9pv` at `1e874d6`. Both tips hold `integration_tests/tests/conftest.py` with the rotated admin password. The file was added in `ba10cb6` and removed in `6f9fcb9`, so the `main` history holds it too.
- Dependency audit (pip-audit 2, PyPI and OSV, pinned files without installation):
  - `requirements/production.txt`: Django 6.0.7 has two GeoDjango advisories, fixed in 6.0.8; the app does not install GeoDjango. Pillow 12.3.0 has 41 advisories, fixed in 13.0.0. sqlparse 0.5.5 has five, fixed in 0.6.0.
  - `requirements/dev.txt` adds Werkzeug 3.0.6, with four Windows-only `safe_join` advisories.
  - `requirements/testing.txt`: pytest 8.3.5 has one advisory, fixed in 9.0.3.
  - `docs/requirements.txt`: no advisory. We did not audit `browser_tests/requirements.txt`, because it gives version ranges, not pins.
- Two review agents read the tree. Their candidates are not verified. The next agent must check each one against the code before the report uses it:
  - photologue's zip upload view in the admin checks staff status only, and it keeps any file name extension;
  - the iframe loader's debug mode writes message data as HTML and does not check the message origin;
  - the labels API checks staff status, not model permissions;
  - the public observation, bed and species pages show records outside public beds;
  - no setting limits Pillow's pixel count, and stored originals keep their EXIF location data;
  - the label editor loads axios from a CDN without a version pin;
  - the `Dockerfile` image runs `runserver` as root;
  - the development image sets `KASVIMUSEO_DEBUG=1`.

### Memory reports

- History scan: started at once after a 0 s wait. Admission 56,635 MiB, final 56,667 MiB. Starting swap 1 MiB, growth 0 MiB. 8 s, exit 0.
- History scan with the unreachable objects: started at once after a 0 s wait. Admission 56,673 MiB, final 56,389 MiB. Starting swap 1 MiB, growth 0 MiB. 9 s, exit 0.
- pip-audit, first run: started at once after a 0 s wait. Admission 56,542 MiB, final 56,414 MiB. Starting swap 1 MiB, growth 0 MiB. 5 s, exit 0. Every audit exited 1 because pip-audit could not write its cache, so this run gave no result.
- pip-audit, second run: started at once after a 0 s wait. Admission 56,618 MiB, final 56,585 MiB. Starting swap 1 MiB, growth 0 MiB. 16 s, exit 0.
- Two smaller history commands ran without the guard: `git fsck --unreachable` and a per-path count of password-shaped lines. The guarded readings just before and after them were 56,673 MiB and 56,542 MiB, with no swap growth.
