# -*- coding: utf-8 -*-
"""Ask ``git`` about the commits the documentation names, and repair them.

A ``:Resolution:`` field, a ``Done`` stage and an archive entry all name a
commit. Each one is written on a task branch, and that branch is rebased onto
``master`` before it lands, so the commit the text names is rewritten and the
text is left pointing at a commit that is on no branch. A dead pointer reads
exactly like a live one.

This module answers two questions about such a pointer:

``classify``
    Where the commit is: on ``master``, on some other reference, or on nothing
    at all. Existence is not the question -- the checkout that wrote the dead
    pointer still holds the object, so ``git cat-file`` says yes to it for as
    long as ``git gc`` leaves it alone.

``successors``
    Which commit on ``master`` the dead one became. Three sources, best first:
    the rewrite log that ``dev/post-rewrite`` records, the patch identity, and
    the commit subject. A pointer this cannot map is reported, never guessed.

Nothing here imports Sphinx, and everything runs on both Pythons: the
documentation build drives ``classify`` on the host's Python 3, ``dev/repoint``
drives both, and ``kasvimuseo/tests/test_commit_pointers.py`` drives them on the
application's Python 2.7. Every function takes the ``git`` it talks to as an
argument, so the tests can answer for it.
"""

from __future__ import unicode_literals

import re
import subprocess

from issue_register import COMMIT_RE

#: Where a pointer's commit is. The first is what the register promises; the
#: last three are the ways it can break.
LANDED = 'landed'      #: on ``master``, which is what a landed pointer means.
PARKED = 'parked'      #: on another reference: a branch in flight, or a tag.
LOST = 'lost'          #: the object is here, but no reference reaches it.
GONE = 'gone'          #: ``git`` does not have the object at all.
MISSING_PATH = 'missing path'  #: the commit is here; the file it must hold is not.

#: The reference every landed pointer is measured against, and where to look
#: for it. A fresh clone has checked out one branch and has the rest as
#: remote-tracking references, so continuous integration has ``origin/master``
#: and no ``master`` at all -- and a check that quietly skips there is a check
#: that does not run where it matters most.
INTEGRATION = 'master'
INTEGRATION_REFS = ('master', 'origin/master')

#: ``dev/post-rewrite`` writes ``<old> <new>`` here, one pair per line, under
#: the git directory. Read by :func:`parse_rewrite_log`.
REWRITE_LOG = 'rewritten-commits'

#: How :func:`successors` found a replacement, worst last. A caller that writes
#: to a file says which of these it trusted.
BY_LOG = 'the rewrite log'
BY_PATCH = 'an identical patch'
BY_SUBJECT = 'the commit subject'


class Pointer(object):
    """One commit the documentation names, and what ``git`` says about it."""

    def __init__(self, source, commit, path=None):
        self.source = source
        self.commit = commit
        #: The file the commit has to hold, for an archive entry; else ``None``.
        self.path = path
        self.verdict = None
        #: The full hash, once ``git`` has resolved the abbreviation.
        self.full = None

    @property
    def is_broken(self):
        """A pointer no reader can follow, whoever they are."""
        return self.verdict in (LOST, GONE, MISSING_PATH)

    @property
    def file(self):
        """The document that holds the pointer, relative to the repository.

        Every source :func:`issue_register.commit_references` writes opens with
        that path and then says where in the file it is, so the first word is
        the file to edit.
        """
        return self.source.split(' ')[0]

    def __repr__(self):
        return str('<Pointer {0} {1}>').format(self.commit, self.verdict)


def pointers(references):
    """``issue_register.commit_references()`` output, as :class:`Pointer`."""
    return [Pointer(source, commit, path) for source, commit, path in references]


def git_runner(repo):
    """A ``git`` that runs in ``repo`` and returns output, or ``None``."""
    def run(args, stdin=None):
        try:
            process = subprocess.Popen(
                ['git'] + list(args), cwd=repo,
                stdin=subprocess.PIPE if stdin is not None else None,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            return None
        output, _errors = process.communicate(
            stdin.encode('utf-8') if stdin is not None else None)
        if process.returncode != 0:
            return None
        return output.decode('utf-8', 'replace').strip()
    return run


def unverifiable(git):
    """Why this checkout cannot answer the question, or ``None`` when it can.

    A checkout that cannot answer has not answered "no", so every caller here
    passes rather than fails on one of these.
    """
    if git(['rev-parse', '--git-dir']) is None:
        return 'this is not a git checkout, or git is not installed'
    if git(['rev-parse', '--is-shallow-repository']) == 'true':
        return 'a shallow clone holds too little history to check against'
    if integration_ref(git) is None:
        return 'this checkout has no {0} to measure against'.format(
            ' and no '.join(INTEGRATION_REFS))
    return None


def integration_ref(git):
    """The branch that means "landed", by whichever name this checkout has it."""
    for ref in INTEGRATION_REFS:
        if git(['rev-parse', '--verify', '--quiet', ref + '^{commit}']):
            return ref
    return None


def classify(pointers, git, integration=None):
    """Set ``verdict`` on every pointer, in four ``git`` calls for the lot.

    A build must not cost one process per pointer, so this asks in batches:
    ``cat-file`` finds the objects that are not here and ``rev-parse`` resolves
    the abbreviations of the rest, then one ``rev-list`` per question separates
    the commits ``master`` reaches from the commits *any* reference reaches.

    The middle answer is the one that matters. A commit on a branch that is
    still in flight is a pointer that has not landed yet, and a commit on a tag
    is a pointer somebody parked there on purpose -- 062 keeps one. A commit on
    nothing is the pointer a rebase killed.
    """
    pointers = list(pointers)
    if not pointers:
        return pointers
    integration = integration or integration_ref(git) or INTEGRATION
    queries = ['{0}:{1}'.format(pointer.commit, pointer.path) if pointer.path
               else '{0}^{{commit}}'.format(pointer.commit)
               for pointer in pointers]
    output = git(['cat-file', '--batch-check'], stdin='\n'.join(queries) + '\n')
    if output is None:
        return None
    for pointer, line in zip(pointers, output.split('\n')):
        if ' missing' in line or ' ambiguous' in line:
            pointer.verdict = MISSING_PATH if pointer.path else GONE
    # The path query answers about a blob, so resolve the commits separately.
    found = [pointer for pointer in pointers if pointer.verdict is None]
    if found:
        resolved = git(['rev-parse'] + ['{0}^{{commit}}'.format(pointer.commit)
                                        for pointer in found])
        if resolved is None:
            return None
        for pointer, line in zip(found, resolved.split('\n')):
            pointer.full = line.strip()
    hashes = sorted(set(pointer.full for pointer in found))
    off_master = _rev_list_except(hashes, [integration], git)
    unreferenced = _rev_list_except(hashes, ['--all'], git)
    if off_master is None or unreferenced is None:
        return None
    for pointer in found:
        if pointer.full not in off_master:
            pointer.verdict = LANDED
        elif pointer.full in unreferenced:
            pointer.verdict = LOST
        else:
            pointer.verdict = PARKED
    return pointers


def _rev_list_except(hashes, exclusions, git):
    """Which of ``hashes`` nothing in ``exclusions`` reaches."""
    if not hashes:
        return set()
    output = git(['rev-list', '--no-walk'] + list(hashes) + ['--not']
                 + list(exclusions))
    if output is None:
        return None
    return set(output.split())


def successors(pointers, git, integration=None, rewrites=None):
    """Map every broken pointer onto the commit that landed, where one did.

    Returns ``{old hash: (new hash, how it was found)}``, and leaves out the
    pointers it cannot map -- a wrong hash is worse than a missing one, because
    it reads as checked.

    The rewrite log is exact: ``git`` handed those pairs to the hook as it
    rewrote them. The patch identity and the subject are inferences, and both
    can fail honestly. A commit that was squashed, split, or dropped has no one
    successor; a conflict resolved during the rebase changes the patch; and a
    subject that appears twice on ``master`` names nothing in particular.
    """
    broken = [pointer for pointer in pointers if pointer.verdict == LOST]
    if not broken:
        return {}
    if rewrites is None:
        rewrites = read_rewrite_log(git)
    integration = integration or integration_ref(git) or INTEGRATION
    log = git(['log', '--format=%H %s', integration])
    if log is None:
        return {}
    landed, subjects = _index(log)
    patches = _PatchIndex(landed, git)
    found = {}
    for pointer in broken:
        if pointer.full in found:
            continue
        match = _follow(pointer.full, rewrites, landed)
        if match:
            found[pointer.full] = (match, BY_LOG)
            continue
        match = patches.match(pointer.full)
        if match:
            found[pointer.full] = (match, BY_PATCH)
            continue
        match = _by_subject(pointer.full, subjects, git)
        if match:
            found[pointer.full] = (match, BY_SUBJECT)
    return found


def _index(log):
    """``git log --format=%H %s`` as the set of commits and subjects it is.

    A subject that appears twice maps to nothing: this register has written
    ``doc: name 067's commit in its Resolution`` on two different commits, so
    "the commit with that subject" is a question with no answer for some of
    them, and the answer has to be no rather than the first one.
    """
    landed = set()
    subjects = {}
    for line in log.split('\n'):
        commit, _space, subject = line.partition(' ')
        if not commit:
            continue
        landed.add(commit)
        subjects[subject] = None if subject in subjects else commit
    return landed, subjects


def read_rewrite_log(git):
    """The ``old -> new`` pairs ``dev/post-rewrite`` has recorded, if any."""
    path = git(['rev-parse', '--git-path', REWRITE_LOG])
    if path is None:
        return {}
    try:
        with open(path) as handle:
            return parse_rewrite_log(handle.read())
    except IOError:
        return {}


def parse_rewrite_log(text):
    """``<old> <new>`` lines, as a mapping. A later line wins over an earlier.

    ``git`` gives the hook one pair per rewritten commit, so a commit rebased
    twice appears twice: once as ``new``, and again as ``old``. The chain is
    followed in :func:`_follow` rather than flattened here, because a log is
    appended to and this is read.
    """
    rewrites = {}
    for line in text.split('\n'):
        parts = line.split()
        if len(parts) >= 2 and _is_hash(parts[0]) and _is_hash(parts[1]):
            rewrites[parts[0]] = parts[1]
    return rewrites


def _follow(commit, rewrites, landed):
    """Walk the rewrite chain to the first commit that is on the branch."""
    seen = set()
    while commit in rewrites and commit not in seen:
        seen.add(commit)
        commit = rewrites[commit]
        if commit in landed:
            return commit
    return None


def _by_subject(commit, subjects, git):
    """The one commit on the branch with the same subject, if there is one.

    A rebase keeps the message, so this survives a conflict that changed the
    patch, and a squash into a commit that kept the subject. It says nothing
    when the subject was used twice.
    """
    subject = git(['log', '-1', '--format=%s', commit])
    if not subject:
        return None
    return subjects.get(subject.strip())


class _PatchIndex(object):
    """The branch's commits, by patch identity: what a rebase kept identical.

    ``git rebase`` uses the same identity to notice that a commit is already
    upstream, so this is that judgement made after the fact. It is also two
    processes per commit on the branch, so the index is built once, and only if
    something actually asks -- most runs have nothing to map.
    """

    def __init__(self, landed, git):
        self.landed = landed
        self.git = git
        self.by_patch = None

    def match(self, commit):
        """The one commit on the branch with this patch, if there is one."""
        wanted = _patch_id(commit, self.git)
        if not wanted:
            return None
        if self.by_patch is None:
            self.by_patch = self._build()
        return self.by_patch.get(wanted)

    def _build(self):
        """Every patch identity on the branch. A repeat maps to nothing.

        A patch that appears twice is a cherry-pick, or a revert of a revert.
        Neither says which one a dead pointer meant, so both are dropped and
        the subject gets its turn.
        """
        by_patch = {}
        for commit in self.landed:
            patch = _patch_id(commit, self.git)
            if patch:
                by_patch[patch] = None if patch in by_patch else commit
        return by_patch


def _patch_id(commit, git):
    """The patch identity of a commit, or ``None`` when it has no patch."""
    diff = git(['diff-tree', '--patch', '--no-color', '--root', commit])
    if not diff:
        return None
    output = git(['patch-id', '--stable'], stdin=diff + '\n')
    return output.split()[0] if output else None


def replace_commit(text, old, new):
    """Rewrite every mention of ``old`` in ``text``, keeping its length.

    The text is written for people, so a commit in it is abbreviated, wrapped
    in double backticks, or in the middle of a sentence. Only whole hex runs
    that ``old`` starts with are touched: the same shape :mod:`issue_register`
    reads a pointer as, so nothing this file does not consider a commit can be
    rewritten by accident.
    """
    def swap(match):
        token = match.group(1)
        if not old.startswith(token):
            return match.group(0)
        return abbreviate(new, len(token))
    return COMMIT_RE.sub(swap, text)


def abbreviate(commit, length):
    """``commit`` at ``length``, made long enough for the check to see it.

    :func:`issue_register.commit_references` reads a commit as a hex run with
    both a digit and a letter in it, which is what keeps ``max-age=31536000``
    out of the register. About one abbreviation in fifty is all digits, and
    writing one would quietly take the pointer out of the check -- this project
    wrote ``7200893`` that way once. So the abbreviation grows by a character
    at a time until it reads as a commit, which also makes it no less unique.
    """
    while length < len(commit):
        candidate = commit[:length]
        if any(char.isdigit() for char in candidate) and \
                any(char.isalpha() for char in candidate):
            return candidate
        length += 1
    return commit


def _is_hash(token):
    return bool(re.match(r'^[0-9a-f]{7,40}$', token))
