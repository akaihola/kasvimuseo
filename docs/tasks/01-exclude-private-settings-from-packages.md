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

- [x] A source distribution and wheel contain no local_settings.py file or marker value.
- [x] Required templates, static files, translations, and migrations remain in both artifacts.
- [x] A clean artifact installs and loads the application with supplied configuration.

## Work done on 2026-10-10

1. `setup.py` lists the private modules in `PRIVATE_MODULES` and drops them in a `build_py` subclass. Both `sdist` and `bdist_wheel` take their module list from `build_py`.
2. `MANIFEST.in` excludes the same files as a second gate for the source distribution.
3. `dev/check-release-artifacts` rejects an artifact that carries a private module, a marker value, or lacks a required data file. `README.rst`, "Before a release", shows the command.
4. `Dockerfile` fails the production image build when a private module reaches the installed package. `.containerignore` also excludes `kajala_settings.py`.
5. `kasvimuseo/tests/test_release_artifacts.py` builds both artifacts from a copy with a planted marker behind a symlink, and loads the wheel with environment configuration.

## Validation on 2026-10-10

- The ten new tests pass in the development image.
- A negative control with the old `setup.py` and the planted symlink put `ylaneenkasvit/local_settings.py` and the marker into the wheel. The checker rejected it. The new `setup.py` produced clean artifacts.
- Machine settings stay in `ylaneenkasvit/`, so the exclusion list is the mechanism. Moving them outside the package is left to [proposal 04](04-track-private-state-exclusions.md).

## Related work

Coordinate the filesystem layout with [proposal 04](04-track-private-state-exclusions.md).
