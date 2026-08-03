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
    install_requires=[line for line in open('requirements/production.txt')],
    tests_require=['mock==2.0.0',
                   'pbr==4.0.2',
                   'pytest==3.5.0',
                   'pytest-django==2.9.1']
)
