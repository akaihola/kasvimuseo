# Keep deployment records private

This note helps contributors identify which repository owns deployment information.

Read [README.rst](../../README.rst), "Site configuration", for the public configuration interface.
The private `kasvimuseo-deployment` repository owns site settings, inventories, and operations records.
Public development instructions must work without access to that repository.
Read [docs/archive.rst](../../docs/archive.rst), "Removed", for pointers to superseded public documents.

Keep machine paths, session identifiers, and tool permissions out of public memory text and metadata.
Preserve originals privately before removing environment-specific records.
