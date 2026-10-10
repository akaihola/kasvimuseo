# Check Photologue migration dependencies

This note helps contributors avoid dependencies on migrations absent from an installed package.

Generate application migrations with `dev/kasvimuseo app manage makemigrations kasvimuseo`.
Check each generated dependency against migrations in the installed package.
Use `showmigrations` to inspect applied migrations.
A model difference reported by `makemigrations` does not mean the database lacks an existing migration.

Older Photologue versions generated cosmetic changes under unscoped `makemigrations`.
[Issue 081](../../docs/issues/081-django-2-1-is-the-next-runtime-upgrade.rst), "Checks", records earlier migration evidence.
Check current package behavior before applying conclusions from an older version.
