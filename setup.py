from setuptools import setup, find_packages


setup(
    name = "ylaneenkasvit",
    version = "0.1",
    packages = find_packages(),
    entry_points = {
        'console_scripts': ['manage = ylaneenkasvit.manage:main'],
    },
    include_package_data=True,
    package_data={'kasvimuseo': ['static/**/*', 'static/**/**/*']},
    install_requires=[line for line in open('requirements/production.txt')],
    tests_require=['mock==2.0.0',
                   'pbr==4.0.2',
                   'pytest==3.5.0',
                   'pytest-django==2.9.1']
)
