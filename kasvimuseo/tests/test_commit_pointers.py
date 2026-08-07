# -*- coding: utf-8 -*-
"""Tests for the commit pointers the documentation writes, and their repair.

The module under test is ``docs/_ext/commit_pointers.py``, which the
documentation build drives on the host's Python 3 and ``dev/repoint`` drives on
either. It is tested here, in the application's Python 2.7 container, for the
reason ``test_issue_register.py`` gives: this is the suite anybody changing
this repository runs.

Every function it has takes the ``git`` it asks as an argument, so these tests
answer for ``git`` rather than build a repository. :class:`FakeGit` is that
answer: a history written as three dictionaries.
"""

from __future__ import unicode_literals

import os
import sys

import pytest

REPO = os.path.dirname(  # kasvimuseo/tests -> kasvimuseo -> repository root
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.insert(0, os.path.join(REPO, 'docs', '_ext'))

import commit_pointers  # noqa: E402  (needs the path above)


#: Every one of these has a letter in its first seven characters, because an
#: abbreviation that does not is one :func:`abbreviate` deliberately
#: lengthens -- see the test that pins that.
MASTER = ['1a11111111111111111111111111111111111111',
          '2b22222222222222222222222222222222222222']
#: Rewritten by a rebase into ``2b22...``: same patch, same subject.
OLD = '3c33333333333333333333333333333333333333'
#: On a tag, on purpose, like the spike issue 062 parked.
TAGGED = '4d44444444444444444444444444444444444444'
#: Written on a branch that has not landed yet.
IN_FLIGHT = '5e55555555555555555555555555555555555555'


class FakeGit(object):
    """A history, as the questions :mod:`commit_pointers` asks about one.

    ``objects`` is what exists at all, ``master`` what the branch reaches, and
    ``referenced`` what any branch or tag reaches. The rest is per-commit
    detail: its subject, its patch, and the file it holds.
    """

    def __init__(self, objects=None, master=None, referenced=None,
                 subjects=None, patches=None, files=None, rewrites='',
                 integration='master'):
        #: Which name this checkout has the integration branch under. A fresh
        #: clone has ``origin/master`` and no ``master``.
        self.integration = integration
        self.objects = set(objects if objects is not None
                           else MASTER + [OLD, TAGGED, IN_FLIGHT])
        self.master = list(master if master is not None else MASTER)
        self.referenced = set(referenced if referenced is not None
                              else self.master + [TAGGED, IN_FLIGHT])
        self.subjects = subjects or {}
        self.patches = patches or {}
        self.files = files or {}
        self.rewrites = rewrites
        self.calls = []

    def __call__(self, args, stdin=None):
        self.calls.append(list(args))
        return self._answer(list(args), stdin)

    def _answer(self, args, stdin):
        if args[:2] == ['rev-parse', '--git-dir']:
            return '.git'
        if args[:2] == ['rev-parse', '--is-shallow-repository']:
            return 'false'
        if args[:2] == ['rev-parse', '--git-path']:
            return '/dev/null/rewritten-commits'
        if args[:3] == ['rev-parse', '--verify', '--quiet']:
            return (MASTER[0] if args[-1].startswith(self.integration + '^')
                    else None)
        if args[0] == 'rev-parse':
            return '\n'.join(self._resolve(query) for query in args[1:])
        if args[:2] == ['cat-file', '--batch-check']:
            return '\n'.join(self._cat_file(line)
                             for line in stdin.strip().split('\n'))
        if args[:2] == ['rev-list', '--no-walk']:
            return self._rev_list(args[2:])
        if args[:1] == ['rev-list']:
            return '\n'.join(self.master)
        if args[:2] == ['log', '-1']:
            return self.subjects.get(args[-1], '')
        if args[0] == 'log':
            return '\n'.join('{0} {1}'.format(commit,
                                              self.subjects.get(commit, ''))
                             for commit in self.master)
        if args[0] == 'diff-tree':
            return self.patches.get(args[-1])
        if args[0] == 'patch-id':
            return '{0} {1}'.format(stdin.strip(), 'x' * 40)
        raise AssertionError('unexpected git call: {0}'.format(args))

    def _resolve(self, query):
        commit = query.split('^')[0]
        return self._full(commit) or ''

    def _full(self, prefix):
        for commit in self.objects:
            if commit.startswith(prefix):
                return commit
        return None

    def _cat_file(self, query):
        if ':' in query:
            commit, path = query.split(':', 1)
            full = self._full(commit)
            if full and path in self.files.get(full, ()):
                return 'abcdef blob 12'
            return '{0} missing'.format(query)
        commit = query.split('^')[0]
        full = self._full(commit)
        return ('{0} commit 42'.format(full) if full
                else '{0} missing'.format(query))

    def _rev_list(self, args):
        wanted = args[:args.index('--not')]
        exclusions = args[args.index('--not') + 1:]
        reached = self.referenced if '--all' in exclusions else set(self.master)
        return '\n'.join(commit for commit in wanted if commit not in reached)


def pointer(commit, path=None, source='docs/issues/099-x.rst ``:Resolution:``'):
    return commit_pointers.Pointer(source, commit, path)


def verdicts(pointers):
    return [item.verdict for item in pointers]


def test_a_commit_on_master_has_landed():
    assert verdicts(commit_pointers.classify([pointer(MASTER[0])],
                                             FakeGit())) == \
        [commit_pointers.LANDED]


def test_an_abbreviated_commit_is_resolved_first():
    assert verdicts(commit_pointers.classify([pointer(MASTER[0][:7])],
                                             FakeGit())) == \
        [commit_pointers.LANDED]


def test_a_commit_on_a_branch_still_in_flight_is_parked():
    """The point of the change: a pointer may name a commit before it lands."""
    assert verdicts(commit_pointers.classify([pointer(IN_FLIGHT)],
                                             FakeGit())) == \
        [commit_pointers.PARKED]


def test_a_commit_held_only_by_a_tag_is_parked():
    """Issue 062 parked a spike on a tag deliberately. That is not rot."""
    assert verdicts(commit_pointers.classify([pointer(TAGGED)],
                                             FakeGit())) == \
        [commit_pointers.PARKED]


def test_a_commit_no_reference_reaches_is_lost():
    """What a rebase leaves behind, and what the old check called present."""
    assert verdicts(commit_pointers.classify([pointer(OLD)], FakeGit())) == \
        [commit_pointers.LOST]


def test_a_commit_git_does_not_have_is_gone():
    assert verdicts(commit_pointers.classify([pointer('deadbee')],
                                             FakeGit())) == \
        [commit_pointers.GONE]


def test_an_archive_entry_names_the_file_the_commit_holds():
    git = FakeGit(files={MASTER[0]: ['docs/gone.rst']})
    landed = commit_pointers.classify(
        [pointer(MASTER[0], 'docs/gone.rst', 'docs/archive.rst')], git)
    missing = commit_pointers.classify(
        [pointer(MASTER[0], 'docs/other.rst', 'docs/archive.rst')], git)
    assert verdicts(landed) == [commit_pointers.LANDED]
    assert verdicts(missing) == [commit_pointers.MISSING_PATH]


def test_only_a_lost_pointer_is_broken():
    parked, lost = commit_pointers.classify(
        [pointer(TAGGED), pointer(OLD)], FakeGit())
    assert not parked.is_broken
    assert lost.is_broken


def test_the_whole_register_costs_four_questions():
    """A build must not cost one process per pointer."""
    git = FakeGit()
    commit_pointers.classify([pointer(MASTER[0]), pointer(MASTER[1]),
                              pointer(OLD), pointer(TAGGED)], git)
    batched = [call for call in git.calls
               if call[0] in ('cat-file', 'rev-list')
               or call[:2] == ['rev-parse', '{0}^{{commit}}'.format(MASTER[0])]]
    assert len([call for call in git.calls if call[0] == 'rev-list']) == 2
    assert len([call for call in git.calls if call[:2]
                == ['cat-file', '--batch-check']]) == 1
    assert len(batched) == 4


def test_a_checkout_that_cannot_answer_says_so_rather_than_failing():
    def no_git(args, stdin=None):
        return None
    assert commit_pointers.unverifiable(no_git) is not None


def test_a_fresh_clone_is_measured_against_origin_master():
    """Continuous integration checks out one branch and keeps the rest as
    ``origin/*``. A check that skipped there would skip where it matters."""
    git = FakeGit(integration='origin/master')
    assert commit_pointers.unverifiable(git) is None
    assert commit_pointers.integration_ref(git) == 'origin/master'
    assert verdicts(commit_pointers.classify([pointer(OLD)], git)) == \
        [commit_pointers.LOST]


def test_a_checkout_with_no_integration_branch_at_all_says_so():
    git = FakeGit(integration='something-else')
    assert 'master' in commit_pointers.unverifiable(git)


def test_a_shallow_clone_cannot_answer():
    def shallow(args, stdin=None):
        return 'true' if args[1] == '--is-shallow-repository' else '.git'
    assert 'shallow' in commit_pointers.unverifiable(shallow)


def test_git_falling_over_mid_question_is_not_a_failed_check():
    def half_git(args, stdin=None):
        return None if args[0] == 'cat-file' else '.git'
    assert commit_pointers.classify([pointer(OLD)], half_git) is None


# The rewrite log, and what a lost pointer became.

def test_the_rewrite_log_is_pairs_of_hashes():
    log = '{0} {1}\nnot a pair\n'.format(OLD, MASTER[1])
    assert commit_pointers.parse_rewrite_log(log) == {OLD: MASTER[1]}


def test_the_rewrite_log_is_followed_through_a_second_rebase():
    """A branch rebased twice writes two pairs, and only the last one landed."""
    middle = '6666666666666666666666666666666666666666'
    git = FakeGit()
    lost = commit_pointers.classify([pointer(OLD)], git)
    found = commit_pointers.successors(
        lost, git, rewrites={OLD: middle, middle: MASTER[1]})
    assert found == {OLD: (MASTER[1], commit_pointers.BY_LOG)}


def test_a_rewrite_chain_that_never_lands_maps_to_nothing():
    git = FakeGit()
    lost = commit_pointers.classify([pointer(OLD)], git)
    assert commit_pointers.successors(lost, git,
                                      rewrites={OLD: IN_FLIGHT}) == {}


def test_an_identical_patch_names_the_commit_that_landed():
    git = FakeGit(patches={OLD: 'the patch', MASTER[1]: 'the patch',
                           MASTER[0]: 'another patch'})
    lost = commit_pointers.classify([pointer(OLD)], git)
    assert commit_pointers.successors(lost, git, rewrites={}) == \
        {OLD: (MASTER[1], commit_pointers.BY_PATCH)}


def test_a_patch_that_landed_twice_names_neither():
    """A cherry-pick, or a revert of a revert: no one successor."""
    git = FakeGit(patches={OLD: 'the patch', MASTER[0]: 'the patch',
                           MASTER[1]: 'the patch'})
    lost = commit_pointers.classify([pointer(OLD)], git)
    assert commit_pointers.successors(lost, git, rewrites={}) == {}


def test_the_subject_answers_when_the_conflict_changed_the_patch():
    git = FakeGit(patches={OLD: 'the patch', MASTER[1]: 'resolved differently'},
                  subjects={OLD: 'fix: the thing', MASTER[1]: 'fix: the thing',
                            MASTER[0]: 'doc: something else'})
    lost = commit_pointers.classify([pointer(OLD)], git)
    assert commit_pointers.successors(lost, git, rewrites={}) == \
        {OLD: (MASTER[1], commit_pointers.BY_SUBJECT)}


def test_a_subject_used_twice_on_master_names_neither():
    """This register has written the same subject on two commits, twice."""
    git = FakeGit(subjects={OLD: 'doc: name the commit',
                            MASTER[0]: 'doc: name the commit',
                            MASTER[1]: 'doc: name the commit'})
    lost = commit_pointers.classify([pointer(OLD)], git)
    assert commit_pointers.successors(lost, git, rewrites={}) == {}


def test_a_squashed_commit_maps_to_nothing_rather_than_to_a_guess():
    """No patch and no subject match: a person has to read the issue."""
    git = FakeGit(patches={OLD: 'the patch', MASTER[0]: 'other',
                           MASTER[1]: 'other again'},
                  subjects={OLD: 'fix: the thing',
                            MASTER[0]: 'feat: everything at once'})
    lost = commit_pointers.classify([pointer(OLD)], git)
    assert commit_pointers.successors(lost, git, rewrites={}) == {}


def test_a_pointer_that_is_not_lost_is_never_re_pointed():
    git = FakeGit(patches={TAGGED: 'the patch', MASTER[1]: 'the patch'})
    parked = commit_pointers.classify([pointer(TAGGED)], git)
    assert commit_pointers.successors(parked, git, rewrites={}) == {}


def test_the_patch_index_is_built_once_and_only_when_it_is_asked():
    """Two processes per commit on master is a price paid at most once."""
    git = FakeGit(patches=dict((commit, commit) for commit in
                               MASTER + [OLD]))
    landed = commit_pointers.classify([pointer(MASTER[0])], git)
    commit_pointers.successors(landed, git, rewrites={})
    assert [call for call in git.calls if call[0] == 'diff-tree'] == []


# Rewriting the text itself.

@pytest.mark.parametrize('text,expected', [
    ('Fixed in 3c33333.', 'Fixed in 2b22222.'),
    ('Fixed in ``3c33333``.', 'Fixed in ``2b22222``.'),
    ('(commit ``3c333333333333``)', '(commit ``2b222222222222``)'),
    ('3c33333 and 3c33333', '2b22222 and 2b22222'),
    ('Fixed in {0}.'.format(OLD), 'Fixed in {0}.'.format(MASTER[1])),
])
def test_a_pointer_is_rewritten_at_the_length_it_was_written(text, expected):
    assert commit_pointers.replace_commit(text, OLD, MASTER[1]) == expected


def test_an_all_digit_abbreviation_is_written_long_enough_to_be_seen():
    """The register reads a commit as a hex run with a digit and a letter.

    An abbreviation that is all digits is one the check cannot see, and this
    project wrote one -- ``7200893`` -- by re-pointing 059 at it.
    """
    landed = '72008933932b0d0093871ef702034c295cf37244'
    assert commit_pointers.replace_commit('Fixed in 3c33333.', OLD, landed) == \
        'Fixed in 72008933932b.'


def test_an_abbreviation_that_already_reads_as_a_commit_is_left_short():
    landed = 'ab00000000000000000000000000000000000000'
    assert commit_pointers.replace_commit('Fixed in 3c33333.', OLD, landed) == \
        'Fixed in ab00000.'


@pytest.mark.parametrize('text', [
    'Another commit 1a11111 entirely.',
    'The path docs/3c33333/x.rst.',
    'A word3c3333333 that is not one.',
    'max-age=31536000 is not a commit.',
])
def test_nothing_else_in_the_prose_is_touched(text):
    assert commit_pointers.replace_commit(text, OLD, MASTER[1]) == text


def test_the_file_to_edit_is_the_first_word_of_the_source():
    assert pointer(OLD).file == 'docs/issues/099-x.rst'
    assert commit_pointers.Pointer('docs/archive.rst', OLD).file == \
        'docs/archive.rst'
