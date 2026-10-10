# Repair commit pointers after rebasing

This note helps contributors repair issue references after a rebase changes commit identifiers.

Read [docs/issues/README.rst](../../docs/issues/README.rst), "A commit named before it lands", for the procedure.
`dev/repoint` reports stale references and `dev/repoint --write` writes supported repairs.
Review the repairs before committing them.
A commit object can exist without any branch or tag reaching it.
The documentation check tests reachability, rather than object existence alone.
