---
name: two-syntax-traps-django15-and-docinfo
description: "Two silent-syntax traps in kasvimuseo: multi-line {# #} renders onto the page, and a blank line inside an issue file's docinfo block hides every field below it"
metadata: 
  node_type: memory
  type: project
  originSessionId: 684c2d70-eddd-4a3b-8e1d-c4b54bb646c5
  modified: 2026-07-30T07:35:49.088Z
---

Two traps that fail silently rather than loudly in this repository:

1. **Django 1.5 `{# ... #}` is single-line only.** A multi-line one is not a
   comment: the text renders onto the page. Use `{% comment %}...{% endcomment %}`
   for anything longer than a line.
2. **A docinfo field body in `docs/issues/NNN-*.rst` may not contain a blank
   line.** `docs/_ext/issue_register.py`'s `parse_docinfo` stops at the first
   blank line, so a multi-paragraph `:Decision:` silently drops every field
   below it and the build fails with "no `:Resolution:` field". Long reasoning
   goes in a body section that `:Decision:` points at (issue 041 does this).
   The same parser also runs in the suite, so `dev/kasvimuseo app test` fails on
   it too -- `test_issue_register.py`, two failures.

**Why:** neither shows up in review; both cost a full docs-build/test cycle.

**How to apply:** after touching a report template, dump the rendered page (a
throwaway pytest that writes `response.content` to `/src/.dev/...` is the
cheapest way — see [[browser-checks-via-static-harness]]) and grep it for
`{%` and `{#`.
