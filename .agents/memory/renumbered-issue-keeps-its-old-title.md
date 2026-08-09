---
name: renumbered-issue-keeps-its-old-title
description: "an issue file renumbered mid-task keeps the old number in its RST title heading, and nothing in the build catches it"
metadata: 
  node_type: memory
  type: project
  originSessionId: 841e008d-f30f-4b5a-a3c3-a9e70339b1a4
  modified: 2026-08-03T20:19:04.567Z
---

Sibling tasks land issue numbers while a task is in flight, so a `docs/issues/`
file often has to be renumbered before it is committed. The filename, the
`index.rst` ranking entry and the `incoming.rst` narrative all get updated
because they are the things being edited — but the **RST title heading on line
2**, `Issue NNN: <slug>`, is easy to miss.

Found on 2026-08-03: `063-the-dragged-museum-number-cannot-be-seen-on-the-ipad.rst`
had been renamed from 058 and its heading still read `Issue 058: The dragged
museum number cannot be seen on the iPad` — pointing at a real and unrelated
058 (the production image's missing data files).

**Why it survives:** nothing checks it. `dev/kasvimuseo docs` builds clean and
all 21 `kasvimuseo/tests/test_issue_register.py` tests pass, because the
register reads the docinfo fields and the *filename*, never the heading text.

**How to apply:** after any renumber, `grep -n "Issue 0" docs/issues/NNN-*.rst`
and check line 2 against the filename. The overline/underline must match the
title's length exactly — a same-width number (058 → 063) leaves them valid, a
different width does not. See [[two-syntax-traps-django15-and-docinfo]] for the
other things in these files that fail silently.
