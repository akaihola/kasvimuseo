# Check template comments and issue fields

This note helps contributors avoid syntax that silently changes rendered pages or issue metadata.

Use `{% comment %}...{% endcomment %}` for template comments longer than one line.
Django's `{# ... #}` syntax supports single-line comments.
Check rendered HTML after changing comments inside scripts.

Keep each issue's metadata block contiguous.
[docs/_ext/issue_register.py](../../docs/_ext/issue_register.py) stops reading fields at the first blank line.
Put longer explanations in a body section and refer to that section from the field.
