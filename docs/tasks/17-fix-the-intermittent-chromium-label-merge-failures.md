# Fix the intermittent chromium label merge failures

This task helps the contributor who keeps the browser suite green find why a drag onto a label of the same species sometimes fails to merge in Chromium.

- Priority: Medium.
- Owner: Any contributor with the browser suite.

## Work

1. Run the two tests below in a loop with `dev/kasvimuseo app browser-test -k "merges_them or by_touch" --browser chromium` until one fails. Record how many runs it took.
2. Read `browser_tests/test_label_editor.py`, `drag` and `touch_drag`, and the editor's drop handling in the label editor JavaScript. Decide whether the second drag starts before the editor has settled after the split, or whether the drop lands outside the merge target.
3. Fix the editor if the editor is at fault. Fix the test if the test is at fault, for example by waiting for the split label before the second drag.
4. Run the loop again for at least twenty passes in Chromium and WebKit.
5. Record the cause and the fix in a new issue record under `docs/issues/`, with `:Related: 045`.

## Evidence

Both tests split number 11 into a new narcissus label and then drag it onto the other narcissus label. On the failing runs the second drag leaves two narcissus labels with one number each.

- `test_a_number_moves_between_labels_by_touch` failed on the CI runs of 2026-10-11 (`3f24d52`, `b02822b`) and 2026-10-14 (`99091e1`).
- `test_dragging_a_number_onto_a_label_of_the_same_species_merges_them` failed on the run of 2026-10-14 (`99091e1`).
- The chromium job passed on the runs of `02d8c7c` and the rerun of `d7bfff1`. WebKit passed on every run.
- No commit between those runs touched the editor or the tests.

## Completion checks

- [ ] The cause is recorded in an issue record.
- [ ] Twenty consecutive runs of both tests pass in Chromium and WebKit.
- [ ] The CI chromium job passes on three consecutive pushes to `main`.