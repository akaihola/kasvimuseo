---
depends-on: []
---

# 01. Exclude private settings from release packages

This proposal helps package maintainers prevent local configuration from entering published application artifacts.

- Priority: High.
- Proposed owner: Package maintainer.

## Proposed work

1. Build releases from clean, tracked source files.
2. Keep machine settings outside the Python package, or explicitly exclude them from every supported packaging path.
3. Add an artifact check that rejects private configuration.
4. Exercise the check with a harmless local_settings.py file and a symlink to that file.

## Review evidence

The review reproduced the leak with a harmless marker. Both `setup.py build_py` and `setup.py sdist` included `ylaneenkasvit/local_settings.py` through a symlink.

[setup.py](../../setup.py) discovers packages from the working tree. [.gitignore](../../.gitignore) and [.containerignore](../../.containerignore) do not control setuptools package contents.

## Completion checks

- [ ] A source distribution and wheel contain no local_settings.py file or marker value.
- [ ] Required templates, static files, translations, and migrations remain in both artifacts.
- [ ] A clean artifact installs and loads the application with supplied configuration.

## Related work

Coordinate the filesystem layout with [proposal 04](04-track-private-state-exclusions.md).
