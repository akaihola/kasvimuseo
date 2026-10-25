# Compile the Finnish messages with Babel

This note helps contributors update a committed `django.mo` file without unrelated changes.

Babel's `pybabel compile` made the committed `kasvimuseo/locale/fi/LC_MESSAGES/django.mo`.
Its `Generated-By` header names the version.
GNU `msgfmt` writes a different header and hash table, so its output differs in every byte.
Compile with the same Babel version:

```bash
uv run --no-project --with babel==2.18.0 pybabel compile -l fi \
    -i kasvimuseo/locale/fi/LC_MESSAGES/django.po \
    -o kasvimuseo/locale/fi/LC_MESSAGES/django.mo
```

Compare the old and the new catalog with Python's `gettext` module.
Only the messages that you added or changed must differ.
