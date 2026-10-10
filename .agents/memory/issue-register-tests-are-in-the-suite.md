# Check issue register changes

This note helps contributors validate changes to existing issue records.

Read [docs/issues/README.rst](../../docs/issues/README.rst), "Metadata fields", before editing metadata.
Run the application suite and documentation build after changing an issue record.
[kasvimuseo/tests/test_issue_register.py](../../kasvimuseo/tests/test_issue_register.py) reads the actual issue directory.
A missing required field or ranking entry can fail application tests without an application code change.
