---
name: browser-checks-via-static-harness
description: "How to check kasvimuseo's Vue pages in a browser even though the browser suite (issue 017) does not exist"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5ad2dc63-546c-40a2-ba5c-46dc33484c94
  modified: 2026-07-31T08:44:21.759Z
---

**Superseded for the label editor since 2026-07-31 (issue 017 is Fixed):** there
is now a committed suite, `browser_tests/`, run by `dev/kasvimuseo app
browser-test`. It drives Playwright from the host against the real application
in its container (own throwaway database + MEDIA_ROOT), vendors the CDN scripts
in `browser_tests/vendor/`, and covers drag/save/photo/print-toggle. Use and
extend that instead of building a harness by hand; the notes below still apply
to *other* pages, and to anything needing WebKit or a print PDF.

Issue 017 meant there was no browser suite, but the Vue pages *can* be checked:
copy the template, strip the Django constructs (`{% load %}`, `{{ ... }}`,
`{% url %}`, `{# #}` — the comments sit inside JS strings), point the data
endpoint at a local `data.json`, serve the directory from a thread inside the
same Playwright script (a backgrounded server is unreachable — see
[[sandbox-reaps-detached-processes]]), and drive Chromium.

**Why:** unpkg/cdnjs are outside the sandbox's allowlist, so vue.min.js,
axios.min.js and sanitize.css must be fetched from
`raw.githubusercontent.com` (sanitize.css lives under `dist/` at tag `v2.0.0`).
The playwright PyPI version must match the Nix browsers at
`$PLAYWRIGHT_BROWSERS_PATH`; the pin lives in the file `$UV_CONSTRAINT` points
at (currently `playwright~=1.61.0`, chromium-1228) — but kandev-spawned agents
get `UV_CONSTRAINT` unset, so read it from
`/nix/store/*-playwright-constraints.txt` (newest generation) instead of probing
versions. See `~/.config/coding-agents/python.md` § Playwright Version Pinning.

Better than stripping the tags by hand: a throwaway pytest module that builds
data with `kasvimuseo/tests/factories.py`, GETs each page with the Django test
client and writes `response.content` plus the label API's JSON into
`/src/.dev/pages/` (the repo is mounted at `/src`). That gives the real rendered
HTML; then only the CDN URLs and the axios data URL need rewriting.

Three gotchas that cost a cycle each:

* `SimpleHTTPRequestHandler`'s `directory` **cannot** be set as a class
  attribute -- `__init__` overwrites it with `os.getcwd()`. Every request 404s
  and the pages still "render", so measurements look plausible and are wrong.
  Subclass and pass `directory=` through `__init__`.
* `is_mobile=True` is what makes an engine honour (or fall back from) the
  viewport meta tag: without it both engines lay out at the context viewport
  width. With it, no tag gives 980px. WebKit and Chromium agree.
* `page.pdf()` honours an explicit `emulate_media(media='screen')` left set
  earlier, so the "printed" PDF silently gets the screen stylesheet. Print from
  a fresh context.

**How to apply:** `uv run -q --with playwright==1.61.0 python3 script.py`.
`pdftotext` is not installed; `--with pypdf` and `PdfReader(...).extract_text()`
read the PDF back.
`page.pdf(prefer_css_page_size=True)` plus `pdfplumber` measures the printed
sheet in cm; `page.emulate_media(media='print')` plus a computed-style read
proves what `@media print` hides. HTML5 drag can be exercised with synthetic
`DragEvent`s carrying a `new DataTransfer()`, but Vue re-renders on nextTick —
wait between dispatching and reading the DOM. Worked example:
commit 4e75b40 (issues 046, 047).
