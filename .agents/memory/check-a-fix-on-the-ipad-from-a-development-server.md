# Check a fix on the iPad from a development server

This note helps contributors give the maintainer a page to check on the garden's iPad.

Production receives application releases rarely, so a recent fix is usually not on the public site.
Serve the integration commit from the base checkout with `dev/kasvimuseo app run --publish`.
The iPad reaches that server over the tailnet on port 8000.
Open `/dev-login/<username>/` first; read [README.rst](../../README.rst), "Development login", for the route.
Check from the server that the page carries the fix and that sampled `/media/` photo URLs answer 200 before asking for the look.
Stop the container after the look.
Issue 056, "What the device said", records the first use of this procedure on 2026-10-12.
