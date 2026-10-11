# Fetch the clean history before the docs build

This note helps contributors with an old clone build the documentation after the public history rewrite.

The documentation names commits of the rewritten public history.
A clone made before the rewrite does not reach those commits, so the build fails on every pointer.
Fetch the rewritten `main` and the tag `interim-062-option-2` into `refs/clean/` from the rewritten repository or from GitHub:

```bash
git fetch https://github.com/akaihola/kasvimuseo.git \
    refs/heads/main:refs/clean/main \
    refs/tags/interim-062-option-2:refs/clean/tags/interim-062-option-2
```

The build then reads the pointers as parked rather than as rot.
A fresh clone of the published history needs no such fetch.
Read [Repair commit pointers after rebasing](repoint-repairs-rebased-hashes.md) for the reachability check.
