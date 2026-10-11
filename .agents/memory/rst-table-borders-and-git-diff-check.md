# Check reStructuredText table borders before committing

This note helps contributors avoid a false conflict-marker report from `git diff --check`.

`git diff --check` reports a line that starts with seven `=` characters as a leftover conflict marker.
A simple table whose first column is seven characters wide produces exactly that line.
Use a first column of six or eight characters, or a `list-table` directive.
Read [docs/issues/deployment-records.rst](../../docs/issues/deployment-records.rst) for a table that passes the check.
