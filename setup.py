from setuptools import setup, find_packages


setup(
    name="ylaneenkasvit",
    version="0.2.1.dev0",
    packages=find_packages(),
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
                          'static/**/*',
                          'templates/**/*']},
    install_requires=[line.strip() for line in open('requirements/production.txt')
                      if line.strip() and not line.lstrip().startswith('#')],
    tests_require=['pytest==4.6.11',
                   'pytest-django==3.10.0']
)
