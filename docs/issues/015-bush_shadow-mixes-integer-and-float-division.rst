=======================================================
Issue 015: bush_shadow mixes integer and float division
=======================================================

:Status: Open
:Severity: Low
:Area: templatetags / front end
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templatetags.py
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``bush.bush_shadow`` builds inline CSS from a mix of integer and float arithmetic::

    reduction = min(planting.width, planting.depth)
    ... width=planting.width - reduction,     # int  -> "6em"
        left=reduction / 2.0,                 # float -> "2.0em"

so the rendered rule contains both ``6em`` and ``2.0em``. The exact strings are pinned by
tests.

Impact
======

Cosmetic inconsistency in generated CSS. Both forms are valid CSS, so the bed map renders correctly today.

Options
=======

1. Leave it -- the output is valid and the tests pin it.
2. Format the numbers consistently if the CSS is ever cleaned up.
