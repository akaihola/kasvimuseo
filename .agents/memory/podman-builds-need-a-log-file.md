# Check development image builds

This note helps contributors keep build evidence and avoid testing an older image after a failed build.

Run the build in the foreground and retain its output:

```bash
dev/kasvimuseo app build > build.log 2>&1
```

Check the command's exit status and log before running tests.
Keep `build.log` outside commits.
A previous image tag can remain available after a failed build.
Read [Use separate development image tags](dev-image-tag-is-shared-between-workspaces.md) when other worktrees build concurrently.
