# -*- coding: utf-8 -*-
"""Tests for the issue register parser behind ``docs/issues/next.rst``.

The parser lives in ``docs/_ext/issue_register.py`` rather than in the
application, because the documentation is built on the host's Python 3 and the
application is not. It is tested here anyway, and written to run on both
Pythons, because this is the suite anybody changing this repository runs; a
check that only the documentation build performs is a check that is discovered
when the documentation build breaks.

The last two tests read the real ``docs/issues/`` -- the parser is only worth
anything if it can read the register as it actually is.
"""

from __future__ import unicode_literals

import os
import sys

import pytest

REPO = os.path.dirname(  # kasvimuseo/tests -> kasvimuseo -> repository root
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(REPO, 'docs')
ISSUES = os.path.join(DOCS, 'issues')

sys.path.insert(0, os.path.join(DOCS, '_ext'))

import issue_register  # noqa: E402  (needs the path above)
from issue_register import IssueRegisterError  # noqa: E402


GOOD = """\
=============================
Issue 099: A well-formed issue
=============================

:Status: Accepted
:Claimed: branch ``feature/whatever``
:Severity: Medium
:Area: tests
:Reported: 2026-07-29
:Source: This test
:Evidence: (none)
:Depends on: 001 -- the first one
    002, 003 -- and two more
:Blocks: (none)
:Related: (none)
:Decision: Ruled on 2026-07-29
:Resolution: (none yet)

Problem
=======

Nothing.
"""


def issue_text(**changes):
    """``GOOD`` with the named fields replaced, or dropped when ``None``."""
    lines = []
    for line in GOOD.split('\n'):
        field = line[1:line.index(':', 1)] if line.startswith(':') else None
        if field in changes:
            value = changes.pop(field)
            if value is None:
                continue
            line = ':{0}: {1}'.format(field, value)
        lines.append(line)
    for field, value in changes.items():
        lines.insert(5, ':{0}: {1}'.format(field, value))
    return '\n'.join(lines)


def parse(name='099-a-well-formed-issue.rst', **changes):
    return issue_register.parse_issue(name, issue_text(**changes))


def test_a_well_formed_issue_reads_its_own_docinfo():
    issue = parse()
    assert issue.number == '099'
    assert issue.title == 'Issue 099: A well-formed issue'
    assert issue.status == 'Accepted'
    assert issue.severity == 'Medium'
    assert issue.claimed == 'branch ``feature/whatever``'
    assert issue.is_actionable is True
    assert issue.needs_decision is False


def test_every_id_in_a_multi_line_depends_on_is_found():
    assert parse().depends_on == ['001', '002', '003']


def test_no_dependencies_means_no_dependencies():
    assert parse(**{'Depends on': '(none)'}).depends_on == []
    assert parse(**{'Depends on': '(none -- it stands alone)'}).depends_on == []


def test_an_undecided_issue_still_needs_a_decision():
    assert parse(Decision='undecided').needs_decision is True


def test_claimed_is_the_one_optional_field():
    assert parse(Claimed=None).claimed is None


@pytest.mark.parametrize('changes, expected', [
    ({'Status': 'Almost done'}, 'not one of'),
    ({'Severity': 'Critical'}, 'not one of'),
    ({'Status': None}, 'no ``:Status:`` field'),
    ({'Depends on': None}, 'no ``:Depends on:`` field'),
    ({'Claimed': ''}, 'is empty'),
    ({'Stauts': 'Open'}, 'unknown field'),
])
def test_a_malformed_issue_is_an_error_not_a_guess(changes, expected):
    with pytest.raises(IssueRegisterError) as error:
        parse(**changes)
    assert expected in str(error.value)


def test_a_file_that_is_not_named_like_an_issue_is_an_error():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.parse_issue('notes.rst', GOOD)
    assert 'NNN-short-slug.rst' in str(error.value)


RANKED = """\
Some prose about the first group.

.. issue-rank::

   002: The reason for 002, which
      wraps onto a second line.
   001: The reason for 001.

Another heading
---------------

.. issue-rank::

   003: The reason for 003.
"""


def test_the_ranking_is_read_in_page_order_across_groups():
    ranking = issue_register.parse_ranking(RANKED)
    assert [number for number, _ in ranking] == ['002', '001', '003']
    assert ranking[0][1] == 'The reason for 002, which wraps onto a second line.'


def test_a_ranking_entry_without_a_reason_is_an_error():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.parse_rank_entries(['004:'])
    assert 'says nothing' in str(error.value)


def test_a_line_that_is_not_an_entry_is_an_error():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.parse_rank_entries(['see the table above'])
    assert 'cannot read' in str(error.value)


def fake(number, status='Open', depends=()):
    return issue_register.Issue(number, number + '-x', 'Issue ' + number, {
        'Status': status,
        'Severity': 'Low',
        'Decision': 'undecided',
        'Depends on': ', '.join(depends) + ' -- because' if depends else '(none)',
    })


ISSUE_SET = {'001': fake('001'),
             '002': fake('002', 'Fixed'),
             '003': fake('003', depends=['002']),
             '004': fake('004', depends=['001']),
             '005': fake('005', 'In progress')}


def test_an_unranked_issue_fails_the_check():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.check_ranking(
            ISSUE_SET, [(n, 'why') for n in ['001', '002', '003', '004']])
    assert 'issue 005 not ranked' in str(error.value)


def test_an_issue_ranked_twice_fails_the_check():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.check_ranking(ISSUE_SET, [('001', 'why'),
                                                 ('001', 'again')])
    assert 'ranked twice' in str(error.value)


def test_a_ranked_issue_with_no_file_fails_the_check():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.check_ranking(ISSUE_SET, [('099', 'why')])
    assert 'does not exist' in str(error.value)


def test_the_queue_keeps_the_ranked_order_and_drops_the_rest():
    ranking = [(number, 'why') for number in sorted(ISSUE_SET)]
    ready, parked = issue_register.build_queue(ISSUE_SET, ranking)
    assert [entry.issue.number for entry in ready] == ['001', '003']
    assert [(entry.issue.number, entry.excluded_because) for entry in parked] == [
        ('002', 'Status is ``Fixed``'),
        ('004', 'waits for 001 (``Open``)'),
        ('005', 'Status is ``In progress``'),
    ]


def linked(number, depends=(), blocks=(), resolution='(none)'):
    """A fake issue that carries both halves of the graph, and a resolution."""
    return issue_register.Issue(number, number + '-x', 'Issue ' + number, {
        'Status': 'Open',
        'Severity': 'Low',
        'Decision': 'undecided',
        'Resolution': resolution,
        'Depends on': '\n'.join(n + ' -- because' for n in depends) or '(none)',
        'Blocks': '\n'.join(n + ' -- because' for n in blocks) or '(none)',
    })


def test_a_graph_that_agrees_with_itself_passes():
    issue_register.check_graph({'001': linked('001', blocks=['002']),
                                '002': linked('002', depends=['001'])})


def test_a_dependency_on_an_issue_with_no_file_is_an_error():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.check_graph({'001': linked('001', depends=['099'])})
    assert 'names issue 099, which has no file' in str(error.value)


def test_a_dependency_the_other_end_does_not_mirror_is_an_error():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.check_graph({'001': linked('001', depends=['002']),
                                    '002': linked('002')})
    assert 'does not name 001 in its ``:Blocks:``' in str(error.value)


def test_an_issue_that_depends_on_itself_is_an_error():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.check_graph({'001': linked('001', depends=['001'])})
    assert 'names 001 itself' in str(error.value)


ARCHIVE = """\
Removed
=======

* ``docs/issues/incoming.rst`` @ ``88455a0`` -- the "Emptied on ..." entries,
  removed 2026-08-04. Each report is a numbered issue file now.
* ``docs/old-plan.rst`` @ ``abc1234`` -- superseded.

Not an entry:

* just a bullet of prose, which the archive is allowed to contain.
"""


def test_an_archive_entry_is_a_path_a_commit_and_a_reason():
    entries = issue_register.parse_archive(ARCHIVE)
    assert [(path, commit) for path, commit, _why in entries] == [
        ('docs/issues/incoming.rst', '88455a0'),
        ('docs/old-plan.rst', 'abc1234'),
    ]
    assert entries[0][2].endswith('numbered issue file now.')


def test_a_bullet_that_opens_with_a_literal_has_to_be_an_entry():
    with pytest.raises(IssueRegisterError) as error:
        issue_register.parse_archive('* ``docs/gone.rst`` -- no commit\n')
    assert 'cannot read this as an archive entry' in str(error.value)


def test_a_resolution_names_the_commits_it_points_at():
    issues = {'001': linked('001', resolution='Fixed in 170412f.'),
              '002': linked('002', resolution='6bbd199, refined in 96fe07d')}
    assert issue_register.commit_references(issues) == [
        ('docs/issues/001-x.rst ``:Resolution:``', '170412f', None),
        ('docs/issues/002-x.rst ``:Resolution:``', '6bbd199', None),
        ('docs/issues/002-x.rst ``:Resolution:``', '96fe07d', None),
    ]


def test_a_number_that_is_only_a_number_is_not_a_commit():
    issues = {'060': linked('060', resolution='stage 2 is max-age=31536000')}
    assert issue_register.commit_references(issues) == []


def test_an_archive_reference_carries_the_path_the_commit_must_hold():
    entries = issue_register.parse_archive(ARCHIVE)
    references = issue_register.commit_references({}, entries)
    assert references[0] == ('docs/archive.rst', '88455a0',
                             'docs/issues/incoming.rst')


def test_the_real_register_graph_agrees_with_itself_in_both_directions():
    issue_register.check_graph(issue_register.load_issues(ISSUES))


def test_the_real_register_parses_and_is_ranked_exactly_once():
    issues = issue_register.load_issues(ISSUES)
    with open(os.path.join(ISSUES, 'index.rst')) as handle:
        ranking = issue_register.parse_ranking(handle.read())
    issue_register.check_ranking(issues, ranking)
    assert len(ranking) == len(issues)


def test_the_real_register_has_something_to_work_on():
    issues = issue_register.load_issues(ISSUES)
    with open(os.path.join(ISSUES, 'index.rst')) as handle:
        ranking = issue_register.parse_ranking(handle.read())
    ready, parked = issue_register.build_queue(issues, ranking)
    assert ready, 'docs/issues/next.rst would render an empty queue'
    assert len(ready) + len(parked) == len(issues)
