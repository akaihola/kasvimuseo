"""Check the vendored inventory and complete license notices for task 7.

The tests check every inventory path, upstream version, and reviewed notice.
They reject missing files, unlisted notices, and altered license text.
"""

from hashlib import sha256
from pathlib import Path

import pytest

from ylaneenkasvit import common_settings

REPO_ROOT = Path(common_settings.__file__).resolve().parent.parent

# Copy, notice, upstream version, version marker, marker file, reviewed SHA-256.
# Update a digest only after checking the complete upstream license text.
COMPONENTS = [
    ('jqm', 'jqm/LICENSE', '1.1.0.2', '1.1.0.2', 'jqm/__init__.py',
     '60cda43023750e0312d7c8b61259c4f17e5eaa4ab85c4a83326e39870a27a610'),
    ('kasvimuseo/static/js/kasvimuseo/fitty.min.js',
     'kasvimuseo/static/js/kasvimuseo/fitty.min.js.LICENSE.txt',
     '2.2.5', 'fitty v2.2.5', None,
     '9664f109c660b7d8261a5670deabea82a4587c10697aca32dcd91c60f33cd4fb'),
    ('kasvimuseo/static/grappelli/jquery/i18n/ui.datepicker-fi.js',
     'kasvimuseo/static/grappelli/jquery/i18n/ui.datepicker-fi.js.LICENSE.txt',
     '1.10.3', 'jQuery UI 1.10.3', None,
     'ba1d100e74583b4a818e58acd7e435473c7ee2ed009cf069dde811d7da914167'),
    ('ylaneenkasvit/templates/grappelli/dashboard/modules/link_list.html',
     'ylaneenkasvit/templates/grappelli/dashboard/modules/link_list.html.LICENSE.txt',
     '2.4.5', 'django-grappelli 2.4.5', None,
     'f01b9c0a1e1b9636cf58a3fd926a7b88811b64188643f20f1ecb398d35023800'),
    ('browser_tests/vendor/vue.min.js',
     'browser_tests/vendor/vue.min.js.LICENSE.txt', '2.6.14', 'Vue.js v2.6.14', None,
     '17fb24bc303763f3fe1911ee24e5225c7ad59f0e3a5d8123e9b730c100a306a6'),
    ('browser_tests/vendor/axios.min.js',
     'browser_tests/vendor/axios.min.js.LICENSE.txt', '1.7.9', '"1.7.9"', None,
     '82761059eaedacb3356803aea8a170d8298609f91b14fc32ee1bfb40d690183c'),
    ('browser_tests/vendor/sanitize.min.css',
     'browser_tests/vendor/sanitize.min.css.LICENSE.txt',
     '2.0.0', 'CC0 Public Domain', None,
     '9bd06b8495290bb450c66d971f24be266247a8cb87a5069132bb368b68992966'),
]


@pytest.fixture(scope='module')
def inventory():
    return (REPO_ROOT / 'docs/third-party-notices.rst').read_text(encoding='utf-8')


def check_inventory(text):
    """Read the inventory's five-column list table and check its files."""
    rows = []
    for line in text.split('.. list-table::', 1)[1].splitlines():
        if line.startswith('   * - '):
            rows.append([line[7:]])
        elif line.startswith('     - '):
            rows[-1].append(line[7:])
        elif line.startswith('       ') and rows:
            rows[-1][-1] += ' ' + line.strip()
        elif line and not line.startswith(' '):
            break
    assert rows.pop(0) == ['Path', 'Upstream', 'Version', 'License', 'Notice file']
    found = []
    for row in rows:
        assert len(row) == 5, row
        path, version, notice = [row[index].strip('`').rstrip('/')
                                 for index in (0, 2, 4)]
        assert (REPO_ROOT / path).exists(), path
        assert (REPO_ROOT / notice).is_file(), notice
        found.append((path, notice, version))
    assert len(found) == len(set(found)), 'The inventory contains duplicate rows'
    assert set(found) == {component[:3] for component in COMPONENTS}


def check_notice(notice, digest):
    actual = sha256((REPO_ROOT / notice).read_bytes()).hexdigest()
    assert actual == digest, f'{notice} differs from the reviewed license text'


def test_the_inventory_matches_the_reviewed_components(inventory):
    check_inventory(inventory)


@pytest.mark.parametrize('path, notice, version, marker, version_file, digest',
                         COMPONENTS, ids=[component[0] for component in COMPONENTS])
def test_the_copy_keeps_its_version_and_complete_notice(
        path, notice, version, marker, version_file, digest):
    assert (REPO_ROOT / path).exists(), path
    assert marker in (REPO_ROOT / (version_file or path)).read_text(encoding='utf-8'), path
    check_notice(notice, digest)


@pytest.mark.parametrize('missing', ['missing-copy', 'jqm/missing.LICENSE.txt'])
def test_an_inventory_row_with_missing_files_fails(inventory, missing):
    row = ('   * - ``missing-copy``\n' if missing == 'missing-copy'
           else '   * - ``jqm/``\n')
    row += '     - Example upstream\n     - ``1.0``\n     - MIT\n'
    notice = 'jqm/LICENSE' if missing == 'missing-copy' else missing
    row += f'     - ``{notice}``\n\n'
    changed = inventory.replace('\nWhat the check', f'\n{row}What the check', 1)
    assert changed != inventory
    with pytest.raises(AssertionError, match=missing):
        check_inventory(changed)


def test_a_truncated_notice_fails(tmp_path, monkeypatch):
    (tmp_path / 'jqm').mkdir()
    notice = tmp_path / 'jqm/LICENSE'
    notice.write_text('Copyright (c) Mike C. Fletcher\n', encoding='utf-8')
    monkeypatch.setitem(globals(), 'REPO_ROOT', tmp_path)
    with pytest.raises(AssertionError, match='differs from the reviewed license text'):
        check_notice('jqm/LICENSE', COMPONENTS[0][-1])


def test_the_notice_files_are_the_only_ones():
    """Reject a notice file without a reviewed inventory entry."""
    found = set()
    for top in ['jqm', 'kasvimuseo', 'browser_tests', 'ylaneenkasvit']:
        for path in (REPO_ROOT / top).rglob('*'):
            if path.is_file() and (path.name == 'LICENSE' or path.name.endswith('.LICENSE.txt')):
                found.add(path.relative_to(REPO_ROOT).as_posix())
    assert found == {component[1] for component in COMPONENTS}
