# Management checks in task worktrees

This note is for agents. It identifies settings for checks that need no development data.

Use ``--settings=ylaneenkasvit.test_settings`` with ``app manage check`` and scoped migration checks.
These settings put media under a temporary path, so the development media link can remain unchanged.
The checks passed during issue 076 without a production dump.
