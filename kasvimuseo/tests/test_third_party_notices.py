# -*- coding: utf-8 -*-
"""Every vendored component keeps its license notice (task 7).

``docs/third-party-notices.rst`` is the inventory: one row per copied file or
package, with the upstream version, the license and the notice file. These
tests tie that page to the tree. Each row's path must exist, its notice file
must exist and name the copyright holder, the copy must still carry the
version the page records, and the page must name both paths. A copy added
without a row, or a row whose files went missing, fails here.
"""

from __future__ import unicode_literals

import io
import os

import pytest

from ylaneenkasvit import common_settings

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(common_settings.__file__)))
INVENTORY = os.path.join(REPO_ROOT, 'docs', 'third-party-notices.rst')

# (copied path, notice file, text the notice must carry, the version the
# copy itself must carry, and the file that carries it)
COMPONENTS = [
    ('jqm', 'jqm/LICENSE', 'Mike C. Fletcher',
     '1.1.0.2', 'jqm/__init__.py'),
    ('kasvimuseo/static/js/kasvimuseo/fitty.min.js',
     'kasvimuseo/static/js/kasvimuseo/fitty.min.js.LICENSE.txt',
     'Rik Schennink', 'fitty v2.2.5', None),
    ('kasvimuseo/static/grappelli/jquery/i18n/ui.datepicker-fi.js',
     'kasvimuseo/static/grappelli/jquery/i18n/'
     'ui.datepicker-fi.js.LICENSE.txt',
     'jQuery Foundation', 'jQuery UI 1.10.3', None),
    ('browser_tests/vendor/vue.min.js',
     'browser_tests/vendor/vue.min.js.LICENSE.txt',
     'Yuxi (Evan) You', 'Vue.js v2.6.14', None),
    ('browser_tests/vendor/axios.min.js',
     'browser_tests/vendor/axios.min.js.LICENSE.txt',
     'Matt Zabriskie', '"1.7.9"', None),
    ('browser_tests/vendor/sanitize.min.css',
     'browser_tests/vendor/sanitize.min.css.LICENSE.txt',
     'CC0 1.0 Universal', 'CC0 Public Domain', None),
]


def read(relative):
    with io.open(os.path.join(REPO_ROOT, relative), encoding='utf-8') as f:
        return f.read()


@pytest.fixture(scope='module')
def inventory():
    return read(os.path.join('docs', 'third-party-notices.rst'))


@pytest.mark.parametrize('path, notice, holder, version, version_file',
                         COMPONENTS, ids=[c[0] for c in COMPONENTS])
def test_the_copy_and_its_notice_exist(path, notice, holder, version,
                                       version_file):
    assert os.path.exists(os.path.join(REPO_ROOT, path)), path
    assert os.path.isfile(os.path.join(REPO_ROOT, notice)), notice
    assert holder in read(notice), '{0} does not name {1}'.format(notice,
                                                                  holder)
    assert version in read(version_file or path), \
        '{0} no longer carries {1}; update docs/third-party-notices.rst' \
        .format(version_file or path, version)


@pytest.mark.parametrize('path, notice, holder, version, version_file',
                         COMPONENTS, ids=[c[0] for c in COMPONENTS])
def test_the_inventory_lists_the_copy(inventory, path, notice, holder,
                                      version, version_file):
    assert '``{0}'.format(path) in inventory, path
    assert '``{0}``'.format(notice) in inventory, notice


def test_the_notice_files_are_the_only_ones():
    """A notice file without a row is a copy nobody inventoried."""
    found = set()
    for top in ['jqm', 'kasvimuseo', 'browser_tests', 'ylaneenkasvit']:
        for root, dirs, files in os.walk(os.path.join(REPO_ROOT, top)):
            for name in files:
                if name == 'LICENSE' or name.endswith('.LICENSE.txt'):
                    found.add(os.path.relpath(os.path.join(root, name),
                                              REPO_ROOT))
    assert found == {c[1] for c in COMPONENTS}
