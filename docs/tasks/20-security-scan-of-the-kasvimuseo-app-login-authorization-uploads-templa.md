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
