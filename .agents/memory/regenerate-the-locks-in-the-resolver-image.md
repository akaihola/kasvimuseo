# Regenerate the locks in the resolver image

This note helps contributors regenerate `requirements/*.txt` with the resolver that made them.

Build the resolver from the base image of `dev/Containerfile`.
[Issue 086](../../docs/issues/086-django-4-2-runtime-upgrade.rst), "Lock generation", names the packages and the tool versions.
Run `pip-compile` with the options in each lock's header.
Compile the locks in this order: production, dev, testing.
Each later input reads an earlier lock.

`pip-compile` keeps a pin that the input still allows.
To move a transitive package, set a floor in the `.in` file.
Then audit each lock with `pip-audit -r <lock> --no-deps --disable-pip`.
[Task 22](../../docs/tasks/22-move-pillow-django-and-sqlparse-past-their-published-advisories.md) records a complete run.
