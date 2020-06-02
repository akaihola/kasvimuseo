from setuptools import setup, find_packages


setup(
    name="ylaneenkasvit",
    version="0.2.1.dev0",
    packages=find_packages(),
    entry_points={
        'console_scripts': ['manage = ylaneenkasvit.manage:main'],
    },
    include_package_data=True,
    package_data={'kasvimuseo': ['static/**/*',
                                 'static/**/**/*',
                                 'templates/**/*',
                                 'templates/**/**/*']},
    install_requires=[line for line in open('requirements/production.txt')],
    tests_require=['mock==2.0.0',
                   'pbr==4.0.2',
                   'pytest==3.5.0',
                   'pytest-django==2.9.1']
)
