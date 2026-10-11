import fnmatch

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py


# Settings modules that belong to one machine and never to a release. They are
# untracked (see .gitignore), but `find_packages()` reads the working tree,
# not the index: `build_py` packages every `*.py` it finds in a package
# directory, and `sdist` takes its module list from `build_py`. So a
# developer's `ylaneenkasvit/local_settings.py` -- a file or a symlink to one
# -- went into both artifacts (task 1). `package_data`/`exclude_package_data`
# cannot help here, because they govern data files only, never modules.
#
# `dev/check-release-artifacts` and the Dockerfile repeat these names, since
# neither can import this file; keep the three lists the same. The test module
# `kasvimuseo/tests/test_release_artifacts.py` builds both artifacts with a
# planted copy to prove this list is applied.
PRIVATE_MODULES = {
    'ylaneenkasvit': ['local_settings*', 'kajala_settings'],
}


class build_py(_build_py):
    """`build_py` that leaves machine-specific settings modules out."""

    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        private = PRIVATE_MODULES.get(package, [])
        return [(pkg, module, path) for pkg, module, path in modules
                if not any(fnmatch.fnmatch(module, pattern)
                           for pattern in private)]


setup(
    name="ylaneenkasvit",
    version="0.2.1.dev0",
    license="BSD-3-Clause",
    license_files=['LICENSE'],
    packages=find_packages(),
    cmdclass={'build_py': build_py},
    entry_points={
        'console_scripts': ['manage = ylaneenkasvit.manage:main'],
    },
    include_package_data=True,
    # `jqm` is the vendored django-jqm (issue 031); it is nothing but the
    # templates and static files listed here, so an install that dropped them
    # would install an empty package and break the login page. See
    # `jqm/README.rst`.
    # These are globs, and `**` is not recursive in either of the mechanisms
    # that read them -- each one matches exactly one path segment. So a file
    # one level deeper needs a line of its own, which is what the fourth entry
    # is: `static/grappelli/jquery/i18n/ui.datepicker-fi.js`, the Finnish date
    # picker grappelli 2.5 asks for and does not ship (upgrade plan Stage 3).
    package_data={'kasvimuseo': ['static/**/*',
                                 'static/**/**/*',
                                 'static/**/**/**/*',
                                 'templates/**/*',
                                 'templates/**/**/*'],
                  'jqm': ['README.rst',
                          'LICENSE',
                          'static/**/*',
                          'templates/**/*']},
    install_requires=[line.strip() for line in open('requirements/production.txt')
                      if line.strip() and not line.lstrip().startswith('#')],
    tests_require=['pytest==8.3.5',
                   'pytest-django==4.11.1']
)
