# Wait for the labels to be drawn

This note helps contributors write label editor browser tests that press on a label.

A label is drawn horizontal until its photo loads, then the editor may flip it vertical.
The flip moves the museum numbers, so a press measured before it misses.
Call `labels_drawn(page)` from [browser_tests/conftest.py](../../browser_tests/conftest.py) after any step that creates a label, before you measure it.
`open_editor` already calls it.

Chromium's memory cache serves a repeated photo without a request, so a development machine never shows the race.
To reproduce a photo-load race, disable the cache with the Chrome DevTools Protocol call `Network.setCacheDisabled` and hold the `/media/` route.
Read [docs/issues/090-a-split-label-flips-when-its-photo-loads.rst](../../docs/issues/090-a-split-label-flips-when-its-photo-loads.rst) for the full record.
