# Check documentation build output

This note helps contributors distinguish a completed documentation build from a queued rebuild.

Run `dev/kasvimuseo docs --clean` and check its output.
The final `docs: .../index.html` line identifies the generated index.
A concurrent invocation can report `docs: a build is already running, marked for rebuild` and exit successfully.
That message means this invocation did not complete a build.
Wait for the active build and check its result before reporting success.
