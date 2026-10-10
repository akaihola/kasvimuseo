# Check browser behavior

This note helps contributors choose browser checks for catalogue pages.

Run `dev/kasvimuseo app browser-test` for the committed suite in [browser_tests/](../../browser_tests/).
Extend that suite when a regression needs a repeatable check.
Use [browser_tests/requirements.txt](../../browser_tests/requirements.txt) for the Playwright package version.
Read [README.rst](../../README.rst), "Continuous integration", for browser installation.

For pages outside the suite, render the actual Django template before checking a static copy.
Keep served test data separate from development data.
Check that all scripts and data requests succeed before measuring layout.
Use a mobile browser context when checking viewport behavior.
Use a fresh context for printed output so previous screen emulation cannot change the result.
