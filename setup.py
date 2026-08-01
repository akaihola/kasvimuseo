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
    package_data={'kasvimuseo': ['static/**/*',
                                 'static/**/**/*',
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
