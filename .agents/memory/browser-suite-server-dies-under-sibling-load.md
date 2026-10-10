# Check browser server failures

This note helps contributors diagnose browser tests that lose their application server.

If tests report `Connection refused`, check the server logs and container state before changing fixtures.
Check system logs for memory exhaustion when the server stops without a shutdown message.
A refused connection alone does not prove memory exhaustion.
Repeat the run after resolving the server failure.

Concurrent worktrees can compete for memory, image tags, and ports.
Use unused `KASVIMUSEO_BROWSER_PORT` and `KASVIMUSEO_PG_PORT` values when running simultaneous suites.
Read [Use separate development image tags](dev-image-tag-is-shared-between-workspaces.md) before building concurrent worktrees.
