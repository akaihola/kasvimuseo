# -*- coding: utf-8 -*-
"""Release artifacts carry no machine-specific settings (task 1).

``find_packages()`` reads the working tree, so an untracked
``ylaneenkasvit/local_settings.py`` -- a file or a symlink to one -- used to go
into both the source distribution and the wheel. ``setup.py`` now drops the
modules named in its ``PRIVATE_MODULES`` from ``build_py``, and
``dev/check-release-artifacts`` rejects an artifact that still carries one.

These tests build both artifacts from a copy of the tracked source with a
planted ``local_settings.py`` behind a symlink, and a planted
``kajala_settings.py`` beside it. Both carry a marker value. The checker must
pass the artifacts, the artifacts must still carry the files that only reach an
install through ``MANIFEST.in`` (issue 058), and the wheel must load the
application with configuration supplied from the environment.

The copy is what keeps the suite honest: it never touches the developer's own
``local_settings.py``, and it never trusts the working tree to be clean.
"""

from __future__ import unicode_literals

import glob
import io
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile

import pytest

from ylaneenkasvit import common_settings

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(common_settings.__file__)))
CHECKER = os.path.join(REPO_ROOT, 'dev', 'check-release-artifacts')
# Joined at run time: this module is itself in the sdist, and the checker
# would otherwise find the marker here.
MARKER = '-'.join(['TASK-1', 'PRIVATE', 'MARKER', '9f3c2a'])

# What the build needs: the packages, setup.py, and what it reads.
SOURCES = ['setup.py', 'MANIFEST.in', 'requirements',
           'kasvimuseo', 'ylaneenkasvit', 'jqm']
# Byproducts of a working tree that are not source.
IGNORE = shutil.ignore_patterns(
    '*.pyc', '__pycache__', '.pytest_cache', 'local_settings*.py',
    'kajala_settings.py', '*.egg-info')


def run(args, **kwargs):
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('stderr', subprocess.STDOUT)
    process = subprocess.run(args, **kwargs)
    return process.returncode, process.stdout.decode('utf-8', 'replace')


@pytest.fixture(scope='module')
def artifacts(tmp_path_factory):
    """Build an sdist and a wheel from a copy with planted private settings.

    Returns ``(source copy, sdist path, wheel path)``.
    """
    root = tmp_path_factory.mktemp('release')
    source = root / 'source'
    source.mkdir()
    for name in SOURCES:
        origin = os.path.join(REPO_ROOT, name)
        if os.path.isdir(origin):
            shutil.copytree(origin, str(source / name), ignore=IGNORE)
        else:
            shutil.copy(origin, str(source / name))

    # The leak the review reproduced: a symlink to a file outside the tree.
    private = root / 'private'
    private.mkdir()
    target = private / 'local_settings.py'
    target.write_text('MARKER = {0!r}\n\n\ndef modify(settings):\n'
                      '    settings["DEBUG"] = True\n'.format(MARKER))
    os.symlink(str(target), str(source / 'ylaneenkasvit' / 'local_settings.py'))
    # And a plain file with a second private name from .gitignore.
    (source / 'ylaneenkasvit' / 'kajala_settings.py').write_text(
        'MARKER = {0!r}\n'.format(MARKER))

    dist = root / 'dist'
    env = dict(os.environ, PYTHONPATH='')
    code, output = run(
        [sys.executable, 'setup.py', '-q', 'sdist', '-d', str(dist),
         'bdist_wheel', '-d', str(dist)],
        cwd=str(source), env=env)
    assert code == 0, output
    [sdist] = glob.glob(str(dist / '*.tar.gz'))
    [wheel] = glob.glob(str(dist / '*.whl'))
    return source, sdist, wheel


def names_in(path):
    if path.endswith('.whl'):
        with zipfile.ZipFile(path) as archive:
            return archive.namelist()
    with tarfile.open(path) as archive:
        # Drop the ``ylaneenkasvit-<version>/`` prefix.
        return ['/'.join(member.name.split('/')[1:])
                for member in archive.getmembers()]


def test_the_planted_files_are_in_the_copy(artifacts):
    """If the planting ever stops working, the other tests pass for nothing."""
    source = artifacts[0]
    planted = source / 'ylaneenkasvit' / 'local_settings.py'
    assert planted.is_symlink()
    assert MARKER in planted.read_text()
    assert MARKER in (source / 'ylaneenkasvit' / 'kajala_settings.py').read_text()


@pytest.mark.parametrize('kind', ['sdist', 'wheel'])
def test_no_private_module_is_in_the_artifact(artifacts, kind):
    path = artifacts[1 if kind == 'sdist' else 2]
    private = [name for name in names_in(path)
               if 'local_settings' in name or 'kajala_settings' in name]
    assert private == []


@pytest.mark.parametrize('kind', ['sdist', 'wheel'])
def test_the_checker_passes_a_clean_artifact(artifacts, kind):
    path = artifacts[1 if kind == 'sdist' else 2]
    code, output = run([sys.executable, CHECKER, '--marker', MARKER, path])
    assert code == 0, output


@pytest.mark.parametrize('kind', ['sdist', 'wheel'])
def test_the_required_data_files_are_in_the_artifact(artifacts, kind):
    """The exclusion is narrow: what issue 058 lists is still there."""
    path = artifacts[1 if kind == 'sdist' else 2]
    names = set(names_in(path))
    for required in ['ylaneenkasvit/templates/base.html',
                     'ylaneenkasvit/locale/fi/LC_MESSAGES/django.mo',
                     'kasvimuseo/locale/fi/LC_MESSAGES/django.mo',
                     'kasvimuseo/migrations/0001_initial.py',
                     'kasvimuseo/static/grappelli/jquery/i18n/'
                     'ui.datepicker-fi.js',
                     'kasvimuseo/templates/kasvimuseo/bed-map.html',
                     'jqm/templates/jqm/login.html',
                     'jqm/README.rst',
                     # The license notices of task 7.
                     'jqm/LICENSE',
                     'kasvimuseo/static/js/kasvimuseo/'
                     'fitty.min.js.LICENSE.txt',
                     'kasvimuseo/static/grappelli/jquery/i18n/'
                     'ui.datepicker-fi.js.LICENSE.txt']:
        assert required in names, required


def test_the_wheel_loads_with_supplied_configuration(artifacts, tmp_path):
    """Install the wheel and load the site settings from the environment.

    ``PYTHONPATH`` is replaced rather than extended, because the development
    image sets it to ``/src`` and the working tree would shadow the install.
    """
    wheel = artifacts[2]
    site = tmp_path / 'site'
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(str(site))
    env = dict(os.environ,
               PYTHONPATH=str(site),
               DJANGO_SETTINGS_MODULE='ylaneenkasvit.ylaneenkasvit_settings',
               # The development image switches debugging on for the working
               # tree. A release gets the production default.
               KASVIMUSEO_DEBUG='',
               KASVIMUSEO_SECRET_KEY='task-1',
               KASVIMUSEO_ALLOWED_HOSTS='example.invalid',
               KASVIMUSEO_DB_NAME='x', KASVIMUSEO_DB_USER='x',
               KASVIMUSEO_DB_PASSWORD='x')
    program = (
        'import django, ylaneenkasvit; django.setup()\n'
        'from django.conf import settings\n'
        'from django.urls import reverse\n'
        'assert ylaneenkasvit.__file__.startswith({site!r}), ylaneenkasvit.__file__\n'
        'assert not settings.DEBUG\n'
        'assert settings.ALLOWED_HOSTS == ["example.invalid"]\n'
        'print(reverse("admin:index"))\n'
    ).format(site=str(site))
    code, output = run([sys.executable, '-c', program],
                       cwd=str(tmp_path), env=env)
    assert code == 0, output
    assert output.strip() == '/admin/'


def test_the_checker_rejects_a_leaked_module(tmp_path):
    """The check itself fails on a wheel that carries the module."""
    wheel = tmp_path / 'ylaneenkasvit-0-py3-none-any.whl'
    with zipfile.ZipFile(str(wheel), 'w') as archive:
        archive.writestr('ylaneenkasvit/local_settings.py', 'MARKER = 1\n')
    code, output = run([sys.executable, CHECKER, str(wheel)])
    assert code == 1
    assert 'private settings module ylaneenkasvit/local_settings.py' in output


def test_the_checker_rejects_a_leaked_marker(tmp_path):
    """A private value under another file name is caught by the marker."""
    sdist = tmp_path / 'ylaneenkasvit-0.tar.gz'
    with tarfile.open(str(sdist), 'w:gz') as archive:
        data = 'SECRET = {0!r}\n'.format(MARKER).encode('utf-8')
        info = tarfile.TarInfo('ylaneenkasvit-0/ylaneenkasvit/site.py')
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
    code, output = run([sys.executable, CHECKER, '--marker', MARKER, str(sdist)])
    assert code == 1
    assert 'contains the marker' in output
