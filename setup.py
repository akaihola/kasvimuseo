from setuptools import setup, find_packages


setup(
    name = "ylaneenkasvit",
    version = "0.1",
    packages = find_packages(),
    entry_points = {
        'console_scripts': ['manage = ylaneenkasvit.manage:main'],
    },
    include_package_data = True,
    install_requires = ['django', 'gunicorn'],
)
