# Check project license artifacts

This note helps contributors keep the project license in application releases.

Read [LICENSE](../../LICENSE) for the project terms and copyright notice.
Read [docs/third-party-notices.rst](../../docs/third-party-notices.rst), "The inventory", for vendored component licenses.

The artifact tests in [kasvimuseo/tests/test_release_artifacts.py](../../kasvimuseo/tests/test_release_artifacts.py) check the project license text and metadata.
[setup.py](../../setup.py) declares the license file.
[Dockerfile](../../Dockerfile) copies it before installation and checks the installed file.

Read [task 6](../../docs/tasks/06-declare-project-license.md), "Review correction, 2026-10-11", for wheel layout coverage.
