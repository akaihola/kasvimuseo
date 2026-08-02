=======================================================
Issue 015: bush_shadow mixes integer and float division
=======================================================

:Status: Rejected
:Severity: Low
:Area: templatetags / front end
:Reported: 2026-07-28
:Source: Test coverage work, branch ``test-coverage_g78``
:Evidence: kasvimuseo/tests/test_templatetags.py
:Depends on: (none)
:Blocks: (none)
:Related: (none)
:Decision: Option 1 -- leave it. Nothing reads the difference: both forms are
    valid CSS lengths, a browser parses ``2.0em`` and ``2em`` identically, and
    the bed map is right today. "Consistently" is also less obvious than it
    sounds -- ``test_templatetags.py``'s third case is a 5 by 5 planting whose
    radius is ``2.5em``, so the halves cannot be printed as integers without
    moving the shadow, and the only consistent formatting left is floats
    everywhere, which turns ``6em`` into ``6.0em`` and reads worse than what is
    there. That would rewrite the three expected strings the tests pin, for a
    diff whose only reader is this issue. Option 2 said "if the CSS is ever
    cleaned up"; no such cleanup is scheduled, and one would touch these
    strings anyway and could carry the formatting with it. The report is
    accurate -- it is the repair that is not worth its churn.
:Resolution: Ruled, no code change. ``bush_shadow`` and the tests that pin its
    output are untouched.

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

What "consistently" would cost
==============================

Option 2 is not the free half of the pair, which is why option 1 was taken.
``test_templatetags.py`` parametrises three plantings, and the third is 5 by 5::

    (5, 5, 'width: 0em;height: 0em;left: 2.5em;top: 2.5em;'
           'box-shadow: 0px 0px 2.5em 2.5em rgba(0, 255, 0, 1);'),

The halves are genuinely fractional, so printing them as integers would move
the shadow rather than tidy it. What is left is floats everywhere -- ``0.0em``,
``6.0em`` -- which is consistent and reads worse than the mixture, plus three
rewritten expected strings. The register's own rule is that a fix deliberately
changes the test that pins today's behaviour; here that edit would buy nothing
a browser or a reader can see.

Nothing forbids picking the formatting up later: if the bed map's CSS is ever
worked on, it touches these strings anyway.
