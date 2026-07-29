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
