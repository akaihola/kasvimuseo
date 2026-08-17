---
name: issue-register-tests-are-in-the-suite
description: "Adding or editing a docs/issues/ file can turn a green suite red: kasvimuseo/tests/test_issue_register.py parses the real register"
metadata:
  node_type: memory
  type: project
---

`kasvimuseo/tests/test_issue_register.py` parses the real `docs/issues/`
directory, not a fixture. Three of its tests load every issue file
(`test_the_real_register_parses_and_is_ranked_exactly_once`,
`test_the_real_register_graph_agrees_with_itself_in_both_directions`,
`test_the_real_register_has_something_to_work_on`), so a malformed or unranked
issue file fails the **unit suite**, not only the docs build.

On 2026-08-17 upgrade Stage 7 ran `app test` (525 passed), then wrote issue 072,
then ran `app coverage` and got `3 failed, 522 passed`. Nothing in the code had
changed between the two runs. The cause was one missing field: `:Resolution:`
is required even on an `Open` issue, and the register wants
`(none yet) -- <why>` rather than nothing.

**Why:** the two runs look like a flaky suite or a coverage-only failure. They
are neither, and the traceback names `docs/_ext/issue_register.py` rather than
anything under test.

**How to apply:** after writing or editing a file in `docs/issues/`, re-run the
suite as well as `dev/kasvimuseo docs`. Two things the register checks that
`README.rst` states and a writer forgets: every field in `REQUIRED_FIELDS` is
present even when the answer is `(none)`, and every issue file has an
`issue-rank` line in `docs/issues/index.rst`. Related:
[[renumbered-issue-keeps-its-old-title]], [[docs-build-lock-exits-zero]].
