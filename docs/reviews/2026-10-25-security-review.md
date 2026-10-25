# Security review of the kasvimuseo app, 2026-10-25

This report is for the maintainer, the contributors and the steward. It records the first security review of the application code ([task 20]). It ranks the findings by impact and likelihood, rechecks the three kasvimuseo findings of the kasvimuseo-deployment review of 2026-10-21, and drafts one issue for each fix worth making. Start with [Do these first](#do-these-first). Nobody changed code, used a credential or sent a request to the live site during the review.

## Urgent

No live credential is in the tree, the history or the ignored files.

Production rotated the signing key, the database password and the admin password on 2026-08-26, according to the deployment records. The rotated admin password remains in the public history. Old task worktrees on the development machine keep rendered pages from before the history rewrite, and the page titles name all three values. The review did not open those pages. Neither copy protects a live system. Read [finding 9](#9-the-rotated-admin-password-stays-in-public-history) and [History and local files](#history-and-local-files).

## Findings at a glance

The "Skill filter" column applies the `security-review` skill's rules, with the verifier's confidence score from 1 to 10. "Passes" means a concrete vulnerability. "Hardening" means a true fact that the skill drops as a hardening gap. "Excluded" means a class of finding that the skill leaves to other processes. Task 20 asks for all of them, so this report keeps them.

| # | Finding | Severity | Skill filter | Fix in | Draft |
| --- | --- | --- | --- | --- | --- |
| 1 | Pillow 12.3.0 in the production lock has 41 published advisories | Medium | Excluded (outdated library) | Both | [K1], [KD1] |
| 2 | The iframe loader trusts messages from any window, and its debug mode writes them as HTML | Medium | Passes (7) | kasvimuseo | [K2] |
| 3 | The admin's zip upload stores files of any extension | Medium where media shares the app's origin, Low in production | Passes narrowly (6) | Both | [K3], [KD2] |
| 4 | Stored originals keep their EXIF location data, and anonymous visitors can download them | Low, Medium if photos of private gardens exist | Passes (4) | Both | [K4], [KD1] |
| 5 | The development harness gives a superuser session to anyone who reaches its port (A1) | Low, Medium on a shared network | Passes (6) | kasvimuseo | [A1 with additions](#a1-with-additions) |
| 6 | Pages load scripts from CDNs without a version pin or an integrity check | Low, High if a CDN or package is compromised | Hardening (3) | kasvimuseo | [K5] |
| 7 | No `SecurityMiddleware` and no password validators (A2) | Low | Hardening | Both | [A2](#a2-and-a3) |
| 8 | Anonymous pages show records outside public beds | Low | Hardening (3) | kasvimuseo | [K6] |
| 9 | The rotated admin password stays in public history (A3) | Low | Hardening | kasvimuseo | [A3](#a2-and-a3) |
| 10 | The `Dockerfile` image runs the development server as root | Low | Hardening (2) | kasvimuseo | [K7] |
| 11 | Other locked packages have advisories that this app does not reach | Low | Excluded (outdated library) | kasvimuseo | [K1], [K8] |
| 12 | The labels API checks staff status, not Label permissions | Low | Hardening (2) | none | [Notes](#notes-without-an-issue) |

## Findings

Line numbers refer to commit `3d3345e` of `main`.

### 1. Pillow in the production lock has advisories

- **What:** [requirements/production.txt] pins Pillow 12.3.0. pip-audit lists 41 advisories for it, all fixed in Pillow 13.0.0. Many are memory-safety bugs in image decoders, for example in the TIFF, JPEG, FlashPix and JPEG 2000 code.
- **Where:** [requirements/production.in] line 9 and [requirements/production.txt]. The decoders run on every upload: in Django's image field check, in photologue's zip upload ([finding 3](#3-the-zip-upload-stores-files-of-any-extension)), in `turn_photo_upright` ([kasvimuseo/models.py:722-771][models.py]) and in photologue's resizing.
- **Impact:** a crafted image that a staff member uploads, on purpose or by mistake, can crash or possibly take over the application process. The deployment review's finding 2 says that a compromise of the application process becomes root on the server.
- **Likelihood:** only staff accounts upload images. The login pages have no rate limit and no password rules ([finding 7](#7-no-securitymiddleware-and-no-password-validators)).
- **Fix:** move to Pillow 13 after a check of photologue 3.20 with it ([K1]). Then deploy ([KD1]). Issue 028 records that photologue broke on an earlier Pillow release, so the check is necessary.

### 2. The iframe loader trusts messages from any window

- **What:** the museum's other site embeds the catalogue with [planted-species-iframe.js]. Its `message` listener checks neither the sender's origin nor the sender window. In debug mode it appends two fields of the message to the page with `innerHTML`.
- **Where:**
  - [planted-species-iframe.js] lines 1-3: the embedding page's own query string switches the debug mode on.
  - Lines 23-30: the debug block, with the `innerHTML` assignment on line 24.
  - Line 31: the frame height comes from the message without a format check.
  - Line 36: the listener, with the `attachEvent` fallback on line 37.
  - [browser_tests/test_iframe_loader.py] tests the frame address only, not the messages.
- **Impact:** a page that a visitor of the museum's other site opens can run script on that site's origin, not on kasvimuseo's. The harm depends on what that site keeps for its visitors, for example logged-in editors. Outside debug mode, any window can change the frame height and the scroll position.
- **Likelihood:** anyone can produce a link with the debug query. Two settings on the other site can block the attack, a `Cross-Origin-Opener-Policy` header or a framing ban. This repository does not show that site.
- **Fix:** accept a message only from the catalogue frame, remove the debug mode, and accept a height in pixels only ([K2]).

### 3. The zip upload stores files of any extension

- **What:** kasvimuseo's `PhotoAdmin` inherits photologue's `upload_zip/` admin view. The view checks each archive entry only with Pillow's `open()` and `verify()`, and then stores the entry under its own file name. Django's image-extension validator does not run on this path. So a file that Pillow accepts keeps any extension, for example one that a browser shows as a web page.
- **Where:**
  - [kasvimuseo/admin.py:370-388][admin.py]: the subclass overrides neither `get_urls` nor `upload_zip`.
  - photologue 3.20 `admin.py` lines 185-215: the route needs staff status only, not the add permission.
  - photologue 3.20 `forms.py` lines 165-216: the name and content checks, and the save.
  - [ylaneenkasvit/ylaneenkasvit_settings.py:17][ylaneenkasvit_settings.py]: `MEDIA_URL` defaults to `/media/`.
  - [ylaneenkasvit/urls.py:58-65][urls.py] and [ylaneenkasvit/media.py:37-43][media.py]: with that default, the app itself serves the media, and the content type follows the file extension.
- **Impact:** where media shares the app's origin, a staff account can store a page that runs script with the session of a superuser who opens it. That crosses the boundary between the gardener accounts and the superusers. Where media comes from a separate host, as the deployment review says production does, the page runs on the media host's origin, and the app's cookies do not go there.
- **Not a finding:** every staff account that exists by design already has the photologue add permission ([kasvimuseo/tests/test_project_urls.py:184-198][test_project_urls.py]). So the missing permission check gives no account a new right today. Nothing in the repository links to the zip upload.
- **Fix:** remove the zip-upload route, or check the extension and the add permission ([K3]). Confirm the separate media origin in production ([KD2]). `SecurityMiddleware` and `nosniff` do not fix this, because the extension already names a web page type.

### 4. Stored originals keep their EXIF location data

- **What:** `turn_photo_upright` keeps all EXIF data except the orientation tag. It stores a file without that tag byte for byte. So GPS location tags of a phone photo stay in the stored original. Photologue's derived sizes drop EXIF, but the originals are public.
- **Where:**
  - [kasvimuseo/models.py:752-755][models.py]: the early return, and the rewrite with the full EXIF block.
  - [ylaneenkasvit/urls.py:34][urls.py]: photologue's public views are routed without a login. `Photo.is_public` defaults to true.
  - photologue 3.20 `templates/photologue/photo_detail.html` line 18 links the original file.
  - [planted-species.html:9][planted-species.html]: an HTML comment holds the original's address, and Django fills it in on the public species sheets.
- **Impact:** any visitor can download an original with its location, date and device tags. A photo taken in a private garden then ties a person to a home address. That is personal data under the GDPR. A photo taken at the museum shows only a public place.
- **Likelihood:** this happens in production today if any stored original has location tags. Nobody has checked the stored originals yet.
- **Fix:** strip the location tags on upload, clean the stored originals, and stop linking the originals ([K4], [KD1]). The size-limit part of this candidate is hardening only: Django's image field and photologue's zip upload reject a decompression bomb before the receiver runs.

### 5. The development login is open to the whole network

This is the deployment review's finding 3 and the application part of its finding 11 (draft A1). It still holds:

- [dev/kasvimuseo:40][dev/kasvimuseo] turns `DEV_LOGIN` on unless the variable is set to empty. Line 39 defaults `ALLOWED_HOSTS` to every host name.
- Lines 300-322 serve on all interfaces with the host network (lines 301, 312 and 319). The `--publish` form on line 305 publishes on all interfaces too.
- `db restore` (lines 92-111) loads a production dump as it is.
- [ylaneenkasvit/dev_login.py:45-68][dev_login.py] logs in any active user by name, superusers included, with a GET request.
- [ylaneenkasvit/common_settings.py:283, 285][common_settings.py] turn `DEBUG` and `DEV_LOGIN` on for any non-empty value, `0` included.

This review adds three details:

- [dev/Containerfile:52][dev/Containerfile] sets `KASVIMUSEO_DEBUG=1` in the image, and the harness never overrides it. Every development server therefore shows technical error pages.
- [ylaneenkasvit/development_settings.py:32][development_settings.py] sets `ALLOWED_HOSTS = ['*']`. The host list that the harness passes has no effect, and the comment at [dev/kasvimuseo:38][dev/kasvimuseo] is wrong.
- `db development` (lines 113-156) gives every account of a derived dump one known password. The login form then accepts real user names, even with `DEV_LOGIN` off. The advice at [README.rst:58-62][README.rst] does not close that.

The verifier scored the combination 6 out of 10.

- **Impact:** anyone who reaches the developer's port gets the admin over a copy of production data, which includes staff names and e-mail addresses. Because the server accepts every host name, a web page that the developer opens can reach a local-only server through DNS rebinding.
- **Not a finding:** nothing in the harness can reach or change production. `media fetch` only reads from the configured fallback host.
- **Fix:** file draft A1 with the [additions](#a1-with-additions) below.

### 6. Pages load unpinned scripts from CDNs

- **What:** the label editor loads axios from unpkg without a version, so it gets each new npm release on the day of release. It also loads Vue 2.6.14 from unpkg and sanitize.css from cdnjs. The jqm base template loads jQuery 1.7.2 and jQuery Mobile 1.1.0 from code.jquery.com. No tag has an `integrity` attribute.
- **Where:**
  - [planting-labels.html] line 16 (sanitize.css), line 335 (axios) and line 336 (Vue).
  - [jqm/templates/jqm/v1_1_0.html][v1_1_0.html] lines 5, 11, 13, 17 and 19.
  - `v1_1_0.html` is the base of `jqm/simple.html`, which the login page, the logout page and the two framed public pages extend.
- **Impact:** whoever controls one of those responses runs script on the kasvimuseo origin. On the label editor that script acts with the staff session. On the login page it can read the password as the person types it.
- **Likelihood:** low. It needs a compromise of npm, the axios package, unpkg, cdnjs or code.jquery.com.
- **Already in place:** [browser_tests/vendor/] holds checked copies of axios 1.7.9, Vue 2.6.14 and sanitize.css 2.0.0. [docs/third-party-notices.rst] records them. The tests serve those copies in place of the CDN.
- **Fix:** serve the checked copies as static files ([K5]).

### 7. No SecurityMiddleware and no password validators

This is the application part of the deployment review's findings 8 and 9 (draft A2). It still holds:

- [ylaneenkasvit/common_settings.py:92-99][common_settings.py] lists no `django.middleware.security.SecurityMiddleware`.
- No settings module sets `AUTH_PASSWORD_VALIDATORS`, `SECURE_PROXY_SSL_HEADER`, `CSRF_TRUSTED_ORIGINS` or any `SECURE_*` setting. The production settings module lives in kasvimuseo-deployment, so this review cannot see whether it sets them.

- **Impact:** Django sends no `nosniff` and no `Referrer-Policy` header, and accepts any password. The deployment review found no concrete exploit.
- **Fix:** file draft A2 as written.

### 8. Anonymous pages show records outside public beds

- **What:** three anonymous report pages answer for any record, not only for public plantings:
  - `BedMap` ([kasvimuseo/views.py:315-321][views.py]) shows any bed, private ones included, with all its plantings, removed ones included.
  - `planted_observation` (lines 285-312) shows any observation by museum number, also one that was never planted. The page shows the beds, the house name and village of the origin, and the history and story texts.
  - `PlantedSpecies` (lines 225-274) filters the beds on `public=True` but not the observations. Nicknames, origins and stories can therefore come from private beds.
- **Not exposed:** no template shows contact data, street addresses, phone numbers or e-mail addresses.
- **Intent:** [docs/index.rst] says that a public bed "is what the public pages list". The decision of issue 001 calls a private planting on the public list a leak. But the admin and the dashboard link these pages for every record, and no test covers a private bed on them.
- **Impact:** anyone can step through bed numbers and museum numbers, and read records that the museum has not put on display. The history text can name the people who grew a plant.
- **Fix:** ask the maintainer what "public" must hide, then filter the anonymous views ([K6]).

### 9. The rotated admin password stays in public history

This is the application part of the deployment review's finding 13 (draft A3). It still holds:

- `git ls-remote` on 2026-10-25 showed the public branches `fix-ipad-label-font-size` at `1cc5996` and `feature/fix-issue-018-run-th-9pv` at `1e874d6`. These are the same tips as on 2026-10-21.
- Both tips hold `integration_tests/tests/conftest.py` with the rotated 3-character admin password.
- Commit `ba10cb6` (2020-01-17) added that file, and commit `6f9fcb9` (2026-07-31) removed it. Both commits are in the history of `main`, so the clean public history holds the value too.
- The old issue file `docs/issues/067-a-correct-password-brings-back-the-login-form.rst` (added in `259c156`, changed in `08f086a` and renamed in `3ce38d1`) names a private home network address. It is reachable from `main` and from the tag `interim-062-option-2`. An address is not a credential.

- **Impact:** low while nobody restores a database dump from before the 2026-08-26 rotation.
- **Fix:** file draft A3 as written.

### 10. The Dockerfile image runs runserver as root

- **What:** the final stage of the [Dockerfile] (lines 115-123) has no `USER` and runs `manage runserver` on all interfaces.
- **Not deployed:** production is an Ansible install from a Git checkout (issue 058). No workflow builds or pushes this image. CI builds [dev/Containerfile] instead.
- **Detail:** Docker reads `.dockerignore`, not [.containerignore]. Under `docker build`, `COPY ylaneenkasvit` (line 48) would copy an untracked private settings module into the builder stage. Lines 100-113 keep it out of the final image.
- **Impact:** a deployment that adopts the image as written faces the internet with Django's development server, running as root.
- **Fix:** label the image as a packaging check, or make it safe to run ([K7]).

### 11. Other locked packages have advisories

- **Django 6.0.7** ([requirements/production.txt]): two advisories, fixed in 6.0.8. Both are in GeoDjango, which this app does not install. Not reached.
- **sqlparse 0.5.5** (production lock, a Django dependency): five advisories, fixed in 0.6.0. They need SQL text from an attacker, and no view hands request data to sqlparse. Not reached.
- **Werkzeug 3.0.6** ([requirements/dev.txt]): four advisories, fixed in 3.1.9. All are about Windows device names in `safe_join`. Development only.
- **pytest 8.3.5** ([requirements/testing.txt]): one advisory, fixed in 9.0.3, about the shared temporary directory on a multi-user machine. Tests only.
- **Fix:** move with Pillow ([K1]), and audit the locks every week ([K8]).

### 12. The labels API checks staff status only

- **What:** `staff_only_api` ([kasvimuseo/views.py:46-65][views.py]) admits any active staff account. Its `post` replaces every label and every planting-to-label link (lines 172-213).
- **Not a finding today:** the decision of [issue 052] makes `is_staff` the gate on purpose. Every staff account that exists by design already holds the Label permissions, and only a superuser can create a new account. CSRF protection is on, and no view is exempt.
- **When it changes:** if the museum adds staff accounts that are limited to some models, those accounts could rewrite all labels. Then require the Label permissions in the API.

## Recheck of the deployment review

kasvimuseo-deployment's review of 2026-10-21 (`docs/reviews/2026-10-21-security-review.md` in that repository) drafted three issues for this repository. Nobody filed them here before this review. All three still hold on `main`:

- **A1, make the development login local-only:** still holds ([finding 5](#5-the-development-login-is-open-to-the-whole-network)). This review adds three details; see [A1 with additions](#a1-with-additions).
- **A2, add the Django security middleware and password rules:** still holds ([finding 7](#7-no-securitymiddleware-and-no-password-validators)). No additions.
- **A3, decide on the stale public branches:** still holds ([finding 9](#9-the-rotated-admin-password-stays-in-public-history)). No additions.

This report does not draft them again. The [Draft issues](#draft-issues) section says how to file them.

The fixed issues still hold:

- 025 (secrets from the environment): [ylaneenkasvit_settings.py] lines 8-14.
- 026 (allowed hosts from the environment): line 15.
- 057 (JSON sessions): [common_settings.py] line 147.
- 059 (secure cookies and the frame policy): lines 98, 113 and 115-116, with the two exempt public views at [kasvimuseo/urls.py] lines 29-31 and 53-56.
- 068 (an optional development login): [ylaneenkasvit/urls.py:51-54][urls.py] and [dev_login.py] line 60.

## History and local files

### History scan

`git log -p` reads commits only. The review scanned every object instead:

1. `git rev-list --all --objects` listed every blob of every branch, remote branch, tag, stash and checkpoint reference: 2,323 blobs.
2. `git fsck --unreachable` added 349 unreachable commits and 1 unreachable blob.
3. A script read each text blob once, and the messages of 1,430 commits. It printed the rule name, the path, the blob, the line number and the shape of the value (its length and character classes), never the value.
4. The rules looked for private keys, cloud and GitHub tokens, JWTs, Ansible Vault blobs, URLs with passwords, password hashes, literal secret and password assignments, password command-line flags, password arguments to `create_user` and `set_password`, private IPv4 addresses and high-entropy string literals.
5. A second pass counted, per path, the lines that put a short literal next to a password, secret or token word.

Results:

- The tree and the history hold no live credential.
- The literal assignments are test fixtures in `kasvimuseo/tests/`, development defaults in [dev/kasvimuseo] and [ylaneenkasvit/test_settings.py], and the `***REMOVED***` markers of the history rewrite in old versions of `ylaneenkasvit/settings.py` and `ylaneenkasvit/ylaneenkasvit_settings.py`.
- The old development database password default was once production's (issue 025). The current default is a different, throwaway value.
- An old version of `planting-labels.html` held a fixed development CSRF token. A CSRF token is not a credential.
- `integration_tests/app/local_settings.py` (commit `ba10cb6`) sets only the language code.
- The rotated admin password and the private network address are in [finding 9](#9-the-rotated-admin-password-stays-in-public-history).

### Ignored and untracked files

The review listed the ignored and untracked files of the base checkout and of every registered worktree, by name only. It did not open a credential file.

- In the base checkout, `.dev`, `media`, `static` and `ylaneenkasvit/local_settings.py` are links into the ignored local state of kasvimuseo-deployment. Its review of 2026-10-21 lists that state by name.
- Five old agent task worktrees from the Django upgrade programme keep `.dev/docs/` build output from before the history rewrite. Some page titles name the credentials that production rotated on 2026-08-26. One task directory also keeps a file named `env.sh`. Only the agent account can read these directories. Delete the build output when the worktrees go. This is a chore on the development machine, not a repository issue.
- The other ignored files are caches, coverage data, editor stubs and the database clusters of the old worktrees, which are mode `700`.

## Dependencies

pip-audit 2 read each pinned file without installing it (`--no-deps --disable-pip`). It asked both PyPI and OSV, and both gave the same advisories.

| File | Package | Version | Advisories | Fixed in | Reached by this app |
| --- | --- | --- | --- | --- | --- |
| [requirements/production.txt] | pillow | 12.3.0 | 41 | 13.0.0 | Yes, through staff uploads ([finding 1](#1-pillow-in-the-production-lock-has-advisories)) |
| [requirements/production.txt] | django | 6.0.7 | 2 | 6.0.8 | No, GeoDjango only |
| [requirements/production.txt] | sqlparse | 0.5.5 | 5 | 0.6.0 | No |
| [requirements/dev.txt] | werkzeug | 3.0.6 | 4 | 3.1.9 | No, Windows only, development only |
| [requirements/testing.txt] | pytest | 8.3.5 | 1 | 9.0.3 | Tests only |
| [docs/requirements.txt] | sphinx, sphinx-autoapi, furo | top-level pins only | 0 | | |

The other production packages have no advisory: asgiref 3.12.1, django-grappelli 5.0.0, django-photologue 3.20, django-sortedm2m 4.0.0, gunicorn 23.0.0, packaging 26.2 and psycopg2-binary 2.9.12.

The review did not audit `browser_tests/requirements.txt`, because it gives version ranges, not pins. The vendored browser scripts are in [finding 6](#6-pages-load-unpinned-scripts-from-cdns).

## Coverage by area

### Authentication and the development login

- Logins go through Django's `ModelBackend` and `LoginView` ([ylaneenkasvit/urls.py:41-46][urls.py]). `LoginView` checks its `next` address.
- The development login exists only when `DEV_LOGIN` is on. Two gates check it: the URL configuration (lines 51-54) and the view ([dev_login.py] line 60).
- Production reaches it only through a non-empty `KASVIMUSEO_DEV_LOGIN`. The deployment sets no such variable, according to the deployment review. The loose parsing is [finding 5](#5-the-development-login-is-open-to-the-whole-network).
- It grants a full session as any active user, superusers included.

### Authorization

| Route | Code | Method | Guard |
| --- | --- | --- | --- |
| `/kasvimuseo/planting-labels/data/` | [views.py] lines 172-213 | POST | `staff_only_api` (lines 46-65), CSRF ([finding 12](#12-the-labels-api-checks-staff-status-only)) |
| `/kasvimuseo/planting-labels/` | [kasvimuseo/urls.py] lines 41-43 | GET | `staff_member_required` |
| `/admin/` model pages | [admin.py] lines 99-388 | POST | the admin login, staff status and model permissions |
| Admin action "planted species report" | [admin.py] lines 66-96 | POST | the change list's permissions; it only redirects |
| `/admin/photologue/photo/upload_zip/` | photologue `admin.py` lines 185-215 | POST | staff status only ([finding 3](#3-the-zip-upload-stores-files-of-any-extension)) |
| `/accounts/login/`, `/accounts/logout/` | [ylaneenkasvit/urls.py:41-46][urls.py] | POST | CSRF |
| `/dev-login/<username>/` | [dev_login.py] lines 45-68 | GET | `DEV_LOGIN` only ([finding 5](#5-the-development-login-is-open-to-the-whole-network)) |
| Photo save receivers | [models.py] lines 722-815 | through admin saves | the admin's guards |
| `/grappelli/` | `grappelli.urls`, included at [ylaneenkasvit/urls.py:15][urls.py] | | [Not reviewed](#not-reviewed) |

Every other route answers GET only and changes nothing. The development login is the only GET that changes state.

### Uploads and image handling

- Only staff upload images, through the photologue admin form or the zip upload ([finding 3](#3-the-zip-upload-stores-files-of-any-extension)).
- The files go to `MEDIA_ROOT/photologue/photos/` through `FileSystemStorage` ([common_settings.py] lines 188-193). Photologue folds the name to ASCII.
- Path traversal is blocked: `django.views.static.serve` cleans the path in [media.py], and `turn_photo_upright` uses `os.path.basename` ([models.py] line 767).
- No setting limits Pillow's pixel count or the upload size. Django's image field and the zip upload reject a decompression bomb before the receiver runs, so this is hardening only. `turn_photo_upright` does not catch `DecompressionBombError` (line 764); a save outside a form would end in an error page. [K4] adds the catch.
- EXIF handling (issue 18's code) is [finding 4](#4-stored-originals-keep-their-exif-location-data).
- Production serves media from a separate host through nginx, according to the deployment review. The repository default serves it from the app ([finding 3](#3-the-zip-upload-stores-files-of-any-extension)).

### Templates

- No template uses `|safe`, `{% autoescape off %}`, `escapejs` or `json_script`. No Python code uses `mark_safe`.
- `format_html` at [admin.py] lines 211, 253 and 356 escapes its arguments, which are integers, `reverse()` addresses and constants.
- The admin renders the help texts of [kasvimuseo/forms.py] (lines 18-42) as safe HTML. They are constant translated strings.
- Vue runs only in [planting-labels.html], with `[[ ]]` delimiters. Staff text reaches it as JSON from the labels API. Inside the Vue root, the server renders only the CSRF token and constant translations.
- The only HTML sink in this repository's JavaScript is the iframe loader ([finding 2](#2-the-iframe-loader-trusts-messages-from-any-window)).

### CSRF, raw SQL, redirects and error pages

- `CsrfViewMiddleware` is on ([common_settings.py] line 95), and no view is exempt. The label editor sends the token from the cookie, so `CSRF_COOKIE_HTTPONLY` stays off on purpose (lines 118-131, issue 059).
- The code has no raw SQL, no `extra()`, no cursor use, no pickle, no YAML loading, no `eval` and no subprocess. Sessions use JSON (line 147).
- Every redirect has a fixed target: [ylaneenkasvit/urls.py:48][urls.py], [dev_login.py] line 68 and [admin.py] line 95. [media.py] lines 42-43 redirect to `MEDIA_FALLBACK_URL`, which is empty unless a developer sets it.
- [404.html] and [500.html] are constant text. `DEBUG` is off unless the environment sets it. The log goes to standard error and holds no secret ([common_settings.py] lines 208-280).

### Settings that reach production

- [ylaneenkasvit/wsgi.py][wsgi.py] line 3 defaults to `ylaneenkasvit.ylaneenkasvit_settings`. That module imports `common_settings` (line 4).
- It reads the secret key and the database credentials from required environment variables (lines 8-14) and the host list from another (line 15).
- [ylaneenkasvit/manage.py][manage.py] line 7 defaults to `ylaneenkasvit.settings`, which is an empty module ([settings.py] line 1). A management command therefore needs `--settings`.
- `development_settings.py` (lines 76-80) applies an untracked `local_settings` module. It is a development module only.
- Production copies its own `ylaneenkasvit_settings.py` from kasvimuseo-deployment into the package. That copy keeps a `local_settings` hook (the deployment review's finding 10). This review cannot see it.
- Both cookies are `Secure` (lines 115-116), and the session cookie is `HttpOnly` by Django's default. `X_FRAME_OPTIONS` is `SAMEORIGIN` (line 113).
- [Finding 7](#7-no-securitymiddleware-and-no-password-validators) lists what is missing.
- The comment at [common_settings.py] lines 137-138 says that the running server still uses the disclosed key (issue 049). The deployment records say that production rotated it on 2026-08-26, so the comment is out of date.

### Dependency versions

See [Dependencies](#dependencies).

## Not reviewed

- **grappelli's lookup and user-switch views:** the related, many-to-many and autocomplete lookups, and the user switch, under `/grappelli/` ([ylaneenkasvit/urls.py:15][urls.py]).
  - Reason: a provider safety check stopped the review session while it read these views. The maintainer decided to leave them for a later review.
  - A later review should check what these staff-only views return to a staff user, and whether this site turns the user switch on.
- **The production settings module:** kasvimuseo-deployment owns it.
- **The museum's other site:** it embeds the catalogue and decides the real impact of [finding 2](#2-the-iframe-loader-trusts-messages-from-any-window). Its source is not in this repository.
- **Smaller remarks from the review agents:** the false-positive check did not cover these, so they are not findings:
  - the label editor puts the `width` and `height` query values into a `<style>` block ([planting-labels.html] lines 89-90; staff only, autoescaped);
  - the species sheet uses the `Referer` header as its "continue" link ([views.py] lines 272-273);
  - the media fallback redirect joins its base and the path without a separator check ([media.py] lines 42-43; development only);
  - [.github/workflows/tests.yml] has no top-level `permissions:` block, and pins some actions by tag, not by commit;
  - `dev/docs-serve` falls back to all interfaces without Tailscale (lines 194-198);
  - the framed species list renders a logout form for a logged-in user (`jqm/simple.html` lines 10-15).

## Method and limits

- The review followed the `security-review` skill over the whole tree, not over one diff.
  - Step 1: two agents looked for candidates, one in the Python code and one in the templates, the scripts and the images.
  - Step 2: eight agents checked one candidate each against the code, and scored it from 1 to 10.
  - Step 3: the skill keeps the candidates that score 8 or more. None scored 8. Task 20 asks for every area, so this report keeps each confirmed fact with its score and its filter class.
- The review read photologue 3.20, Django 6.0.7 and Pillow 12.3.0 from an installed copy that matches [requirements/production.txt].
- The scans printed value shapes, never values. The rotated admin password and the old secrets never reached the review output.
- A provider safety check stopped one response of the first session; see [Not reviewed](#not-reviewed). The maintainer then asked for this defensive write-up, without attack details.
- The review made one read request to GitHub (`git ls-remote`) and asked PyPI and OSV for advisories. It made no request to the live site, ran no test suite and started no service.
- [Task 20] records the memory readings of each heavy command.

## Notes without an issue

- [Finding 12](#12-the-labels-api-checks-staff-status-only): revisit it when the museum adds staff with limited permissions.
- The old build output in the task worktrees: delete it with the worktrees ([History and local files](#history-and-local-files)).
- The out-of-date comment at [common_settings.py] lines 137-138: correct it when [A2](#a2-and-a3) touches the file.

## Do these first

1. **[K1], then [KD1]:** move Pillow to 13 and deploy it. Production decodes every upload with a release that has 41 published advisories.
2. **[K4], with its production step in [KD1]:** strip location tags from the originals. First count the stored originals that have location tags, because a positive count means the exposure is real today.
3. **[K2]:** check the message origin in the iframe loader. The fix is small, and any visitor of the museum's other site can meet the attack.
4. **[K3] and [KD2]:** remove the zip upload and confirm the separate media origin.
5. **File A1 with the additions, A2 and A3** from the deployment review.
6. Then [K8], [K5], [K6] and [K7], in that order.

## Draft issues

Each draft has a title, the work, the acceptance criteria and the checks. File the K drafts in this repository's [TASKS.md]. File the KD drafts in kasvimuseo-deployment's `TASKS.md`. This report files none of them.

### K1. Move the locks past the published advisories

Fixes findings 1 and 11. File in kasvimuseo.

Work:

1. Check that photologue 3.20 runs with Pillow 13: its upload, its resizing and its effects. Issue 028 records the last Pillow break.
2. Set Pillow to 13.0.0 or later in [requirements/production.in], Django to 6.0.8 or later, and sqlparse to 0.6.0 or later.
3. Set Werkzeug to 3.1.9 or later in the development lock, and pytest to 9.0.3 or later in the testing lock. Record a reason for any package that cannot move.
4. Regenerate the three locks the way issue 027 records, and refresh [docs/dependency-inventory.rst] with `dev/deps-inventory`.

Acceptance:

- pip-audit reports no advisory for the three locks, or the task names each remaining advisory with a reason.
- The application suite and the browser suite pass.

Checks:

- `uvx pip-audit -r requirements/production.txt --no-deps --disable-pip`, and the same for `requirements/dev.txt` and `requirements/testing.txt`.
- `dev/kasvimuseo app test` and `dev/kasvimuseo app browser-test`.

### K2. Check the message origin in the iframe loader

Fixes finding 2. File in kasvimuseo.

Work:

1. In [planted-species-iframe.js], ignore a message unless its origin is the catalogue's origin and its source is the frame's window.
2. Remove the debug mode and its `document.write`. If the maintainer wants to keep it, write its text with `textContent`.
3. Accept a height only as digits followed by `px`, with an upper limit.
4. Tell the operators of the museum's other site that the script changed.

Acceptance:

- A message from another window changes neither the frame height nor the page, with or without the debug query.
- A message from the catalogue frame still sets the height.
- Markup in a plant name shows as text.

Checks:

- New cases in [browser_tests/test_iframe_loader.py], run with `dev/kasvimuseo app browser-test`.

### K3. Store only image files from the zip upload

Fixes the application part of finding 3. File in kasvimuseo.

Work:

1. Override `get_urls` in kasvimuseo's `PhotoAdmin` ([admin.py] line 370) so that it drops `upload_zip/`. Nothing links to it.
2. If the maintainer wants to keep the zip upload, check the add permission, and accept only the extensions `jpg`, `jpeg`, `png`, `gif` and `webp`.
3. Make `serve_media` ([media.py]) answer 404 for a file whose extension is not an image type.

Acceptance:

- The admin has no zip-upload route, or the route refuses a user without the add permission and an entry with another extension.
- `serve_media` answers 404 for a file with an extension that is not an image type.

Checks:

- New tests in `kasvimuseo/tests/test_admin.py` and `kasvimuseo/tests/test_project_urls.py`, run with `dev/kasvimuseo app test`.

### K4. Strip location data from uploaded originals

Fixes finding 4 and the receiver gap under [Uploads and image handling](#uploads-and-image-handling). File in kasvimuseo.

Work:

1. In `turn_photo_upright` ([models.py] lines 722-771), remove the GPS block and the owner and serial number tags from every new upload, also from one without an orientation tag. Keep `DateTimeOriginal` and the orientation fix.
2. Catch `Image.DecompressionBombError` in the same receiver, and give the admin a form error.
3. Add a management command that strips the same tags from stored originals. Give it a mode that only counts the tagged files.
4. Override photologue's `photo_detail.html`, so that it links the display size, not the original. Delete the commented address at [planted-species.html:9][planted-species.html].
5. Record in [task 19] that the receiver now does more than the orientation work-around, so that removing the work-around keeps the tag removal.

Acceptance:

- An upload with location tags is stored without them, with or without an orientation tag. `DateTimeOriginal` stays.
- No public page names the address of an original.
- The counting mode of the command reports the number of tagged originals and changes nothing.

Checks:

- New cases in `kasvimuseo/tests/test_photo_orientation.py` and `kasvimuseo/tests/test_templates.py`, run with `dev/kasvimuseo app test`.
- `dev/kasvimuseo app manage <command> --count` on a development copy.

### K5. Serve the page scripts from static files

Fixes finding 6. File in kasvimuseo.

Work:

1. Copy the checked axios, Vue and sanitize.css files from [browser_tests/vendor/] into `kasvimuseo/static/`. Point [planting-labels.html] at them.
2. Do the same for jQuery 1.7.2 and jQuery Mobile 1.1.0 in [v1_1_0.html].
3. Add the files to [docs/third-party-notices.rst] and to the `package_data` of `setup.py`, as fitty is.
4. Remove the CDN substitution from `browser_tests/conftest.py`.

Acceptance:

- No template loads a script or a stylesheet from another origin.
- The release artifact check and the browser suite pass.

Checks:

- `! grep -rnE '(src|href)="https?://' --include='*.html' kasvimuseo/templates jqm/templates ylaneenkasvit/templates`, with each remaining match reviewed.
- `python3 dev/check-release-artifacts dist/*.tar.gz dist/*.whl` and `dev/kasvimuseo app browser-test`.

### K6. Decide what the anonymous pages hide

Fixes finding 8. File in kasvimuseo.

Work:

1. Ask the maintainer whether private beds, removed plantings and observations that were never planted must stay hidden from anonymous visitors. Record the answer in the issue.
2. If they must, show only public, current plantings in `BedMap`, `planted_observation` and `PlantedSpecies` ([views.py]) for anonymous visitors, and answer 404 otherwise. Staff keep seeing every record, so the dashboard and the admin links keep working.

Acceptance:

- The issue records the maintainer's decision.
- If the decision is to hide: an anonymous visitor gets 404 for a private bed's map and for an observation that is not in a public bed; the species sheet leaves out nicknames and stories from private beds; a staff member still sees all of them.

Checks:

- New cases in `kasvimuseo/tests/test_views.py`, run with `dev/kasvimuseo app test`.

### K7. Say what the Dockerfile image is for

Fixes finding 10. File in kasvimuseo.

Work:

1. Ask the maintainer whether the image is only a packaging check. Issue 058 left that open.
2. If it is, say so in a header comment of the [Dockerfile] and in [README.rst] "Before a release".
3. If it must run, add a non-root `USER` in the final stage, and run gunicorn instead of `runserver`.
4. Add a `.dockerignore` with the rules of [.containerignore], and make `kasvimuseo/tests/test_ignore_rules.py` check that the two files agree.

Acceptance:

- The `Dockerfile` says what the image is for.
- A runnable image does not run as root.
- The two ignore files agree.

Checks:

- `dev/kasvimuseo app test -k ignore_rules`.
- If the image runs: `podman image inspect --format '{{.Config.User}}' <image>` prints a non-root user.

### K8. Audit the locks for advisories every week

Fixes the process gap behind findings 1 and 11. File in kasvimuseo.

Work:

1. Add a step to [.github/workflows/weekly.yml] that runs a pinned pip-audit 2 release over the three locks, with `--no-deps --disable-pip`.
2. Let the step fail the weekly run when a lock has an advisory. Put the advisory identifiers in the job summary.

Acceptance:

- The weekly run fails while a lock holds a package with a published advisory, and passes after [K1].

Checks:

- A manual run of the weekly workflow before and after [K1].

### A1 with additions

Fixes finding 5. File the deployment review's draft A1 in kasvimuseo, as written there, with these additions:

1. Remove `KASVIMUSEO_DEBUG=1` from [dev/Containerfile:52][dev/Containerfile]. Let `dev/kasvimuseo` pass `DEBUG` only when the developer asks for it.
2. Make [ylaneenkasvit/development_settings.py:32][development_settings.py] read the host list with `hosts_from_env`, with `localhost` and `127.0.0.1` as the default. Correct the comment at [dev/kasvimuseo:38][dev/kasvimuseo].
3. Bind the `--publish` form ([dev/kasvimuseo:305][dev/kasvimuseo]) to `127.0.0.1` too.
4. Make `db development` choose a random password for each run, and print it once.
5. Correct [README.rst:58-62][README.rst]: switching `DEV_LOGIN` off does not close the shared password.

Extra acceptance:

- A development server started with no variables runs with `DEBUG` off and answers only on the loopback address.
- `KASVIMUSEO_DEV_LOGIN=0` leaves the route off.

### A2 and A3

File the deployment review's drafts A2 and A3 in kasvimuseo, as written there. This review adds nothing to them.

### KD1. Deploy K1 and K4 and clean the originals

File in kasvimuseo-deployment. Depends on [K1] and [K4].

Work:

1. Deploy the release that holds [K1] and [K4].
2. Run the [K4] command on production in its counting mode, and record the count.
3. If the count is not zero, run the command to strip the tags, and run the counting mode again.

Acceptance:

- The installed versions on production match [requirements/production.txt].
- The counting mode reports zero tagged originals.

Checks:

- The verify play of kasvimuseo-deployment.
- The count, before and after, in the operations record.

### KD2. Confirm that the media host serves images only

Fixes the deployment part of finding 3. File in kasvimuseo-deployment. It extends that repository's draft D7, which adds `nosniff` to the media host.

Work:

1. Confirm that production's `KASVIMUSEO_MEDIA_URL` is an absolute address on another host than the application.
2. Make the nginx media server answer only image types, or send every other type as a download.
3. List the stored files under `photologue/photos/` whose extension is not an image type. Remove them after the maintainer looks at the list.

Acceptance:

- The application host routes no `/media/` path.
- The media host does not show a file of another type as a page.
- The list is empty, or the maintainer has reviewed it.

Checks:

- The verify play of kasvimuseo-deployment.

[task 20]: ../tasks/20-security-scan-of-the-kasvimuseo-app-login-authorization-uploads-templa.md
[task 19]: ../tasks/19-remove-the-orientation-work-around.md
[TASKS.md]: ../../TASKS.md
[issue 052]: ../issues/052-saving-the-label-editor-does-nothing-without-an-admin-cookie.rst
[docs/index.rst]: ../index.rst
[docs/third-party-notices.rst]: ../third-party-notices.rst
[docs/dependency-inventory.rst]: ../dependency-inventory.rst
[docs/requirements.txt]: ../requirements.txt
[README.rst]: ../../README.rst
[Dockerfile]: ../../Dockerfile
[.containerignore]: ../../.containerignore
[.github/workflows/tests.yml]: ../../.github/workflows/tests.yml
[.github/workflows/weekly.yml]: ../../.github/workflows/weekly.yml
[requirements/production.in]: ../../requirements/production.in
[requirements/production.txt]: ../../requirements/production.txt
[requirements/dev.txt]: ../../requirements/dev.txt
[requirements/testing.txt]: ../../requirements/testing.txt
[dev/kasvimuseo]: ../../dev/kasvimuseo
[dev/Containerfile]: ../../dev/Containerfile
[browser_tests/vendor/]: ../../browser_tests/vendor/
[browser_tests/test_iframe_loader.py]: ../../browser_tests/test_iframe_loader.py
[common_settings.py]: ../../ylaneenkasvit/common_settings.py
[ylaneenkasvit_settings.py]: ../../ylaneenkasvit/ylaneenkasvit_settings.py
[development_settings.py]: ../../ylaneenkasvit/development_settings.py
[ylaneenkasvit/test_settings.py]: ../../ylaneenkasvit/test_settings.py
[settings.py]: ../../ylaneenkasvit/settings.py
[manage.py]: ../../ylaneenkasvit/manage.py
[wsgi.py]: ../../ylaneenkasvit/wsgi.py
[urls.py]: ../../ylaneenkasvit/urls.py
[media.py]: ../../ylaneenkasvit/media.py
[dev_login.py]: ../../ylaneenkasvit/dev_login.py
[404.html]: ../../ylaneenkasvit/templates/404.html
[500.html]: ../../ylaneenkasvit/templates/500.html
[kasvimuseo/urls.py]: ../../kasvimuseo/urls.py
[views.py]: ../../kasvimuseo/views.py
[admin.py]: ../../kasvimuseo/admin.py
[models.py]: ../../kasvimuseo/models.py
[kasvimuseo/forms.py]: ../../kasvimuseo/forms.py
[test_project_urls.py]: ../../kasvimuseo/tests/test_project_urls.py
[planted-species-iframe.js]: ../../kasvimuseo/static/js/kasvimuseo/planted-species-iframe.js
[planting-labels.html]: ../../kasvimuseo/templates/kasvimuseo/reports/planting-labels.html
[planted-species.html]: ../../kasvimuseo/templates/kasvimuseo/reports/planted-species.html
[v1_1_0.html]: ../../jqm/templates/jqm/v1_1_0.html
[K1]: #k1-move-the-locks-past-the-published-advisories
[K2]: #k2-check-the-message-origin-in-the-iframe-loader
[K3]: #k3-store-only-image-files-from-the-zip-upload
[K4]: #k4-strip-location-data-from-uploaded-originals
[K5]: #k5-serve-the-page-scripts-from-static-files
[K6]: #k6-decide-what-the-anonymous-pages-hide
[K7]: #k7-say-what-the-dockerfile-image-is-for
[K8]: #k8-audit-the-locks-for-advisories-every-week
[KD1]: #kd1-deploy-k1-and-k4-and-clean-the-originals
[KD2]: #kd2-confirm-that-the-media-host-serves-images-only
