# -*- coding: utf-8 -*-
"""Sphinx directives that build the issue tables from the issue files.

Three directives, all reading ``docs/issues/NNN-*.rst`` at build time so no
table is a hand-maintained copy of a status:

``issue-rank``
    In :doc:`index <../issues/index>`, one per group of the suggested order.
    Its body *is* the machine-readable ranking -- ``NNN: why it is here``, next
    to the prose that argues for the group -- and it renders as that group's
    table.

``issue-queue`` / ``issue-parked``
    In ``next.rst``: what is ready to pick up, and what is deliberately not.

The parsing and the rules live in ``issue_register.py``, which imports nothing
outside the standard library and is tested by the application's own suite. A
malformed field, or a ranking that does not list every issue exactly once,
raises and so fails the build -- which is the point of generating this at all.
"""

from __future__ import unicode_literals

import io
import os
import subprocess

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import StringList
from sphinx.errors import ExtensionError
from sphinx.util import logging

import issue_register
from issue_register import IssueRegisterError

INDEX_NAME = 'index.rst'
ARCHIVE_NAME = 'archive.rst'

logger = logging.getLogger(__name__)

#: Read once per build, in ``builder-inited``, and used by every directive.
#: Deliberately not on ``env``: it is derived from files Sphinx already tracks
#: as dependencies, so there is nothing to carry over to the next build.
_register = None


class Register(object):
    """Everything the directives need, read once per build."""

    def __init__(self, srcdir):
        self.issues_dir = os.path.join(srcdir, 'issues')
        self.issues = issue_register.load_issues(self.issues_dir)
        self.index_path = os.path.join(self.issues_dir, INDEX_NAME)
        with io.open(self.index_path, encoding='utf-8') as handle:
            self.ranking = issue_register.parse_ranking(
                handle.read(), 'docs/issues/' + INDEX_NAME)
        issue_register.check_ranking(self.issues, self.ranking,
                                     'docs/issues/' + INDEX_NAME)
        issue_register.check_graph(self.issues)
        self.ready, self.parked = issue_register.build_queue(self.issues,
                                                             self.ranking)
        self.archive_path = os.path.join(srcdir, ARCHIVE_NAME)
        self.archive = self._read_archive()

    def _read_archive(self):
        """The archive page, or nothing if it is not there yet.

        Absent is not an error: the page is written by whoever first removes a
        document, and this check has to be able to land before that happens.
        """
        if not os.path.exists(self.archive_path):
            return []
        with io.open(self.archive_path, encoding='utf-8') as handle:
            return issue_register.parse_archive(handle.read(),
                                                'docs/' + ARCHIVE_NAME)

    @property
    def paths(self):
        """Every file the generated tables are derived from."""
        paths = [self.index_path] + [
            os.path.join(self.issues_dir, issue.docname + '.rst')
            for issue in self.issues.values()]
        if os.path.exists(self.archive_path):
            paths.append(self.archive_path)
        return paths


def load_register(app):
    """Read the register, turning its own errors into build failures."""
    global _register
    try:
        _register = Register(app.srcdir)
        verify_commits(os.path.dirname(str(app.srcdir)),
                       issue_register.commit_references(_register.issues,
                                                        _register.archive))
    except IssueRegisterError as error:
        raise ExtensionError('issue register: {0}'.format(error))


def verify_commits(repo, references):
    """Fail the build when a commit the documentation names cannot be read.

    A ``:Resolution:`` names the commit that fixed the issue and an archive
    entry names a commit that still holds a removed file, so both are promises
    about this repository's history -- and both are written on a task branch
    whose commits are rewritten when it is rebased onto ``master``. A pointer
    that died in a rebase is indistinguishable from a correct one by reading.

    One ``git cat-file --batch-check`` for the lot: a build must not cost
    seventy processes. Where the history is not there to check -- no ``git``, a
    shallow clone, an unpacked tree -- this reports that it skipped and passes,
    because a checkout that cannot answer the question has not answered "no".
    """
    if not references:
        return
    reason = _unverifiable(repo)
    if reason:
        logger.info('issue register: not checking %d commit reference(s): %s',
                    len(references), reason)
        return
    queries = ['{0}:{1}'.format(commit, path) if path else
               '{0}^{{commit}}'.format(commit)
               for _source, commit, path in references]
    output = _git(repo, ['cat-file', '--batch-check'],
                  stdin='\n'.join(queries) + '\n')
    if output is None:
        logger.info('issue register: not checking %d commit reference(s): '
                    'git cat-file did not run', len(references))
        return
    lines = output.split('\n')
    for (source, commit, path), line in zip(references, lines):
        if ' missing' not in line and ' ambiguous' not in line:
            continue
        if path:
            raise IssueRegisterError(
                '{0}: ``{1}`` is not in commit {2}. The archive points at the '
                'commit that still holds the removed file, and it has to be one '
                'that is already on master -- a commit made on the branch that '
                'does the removal does not survive its rebase'
                .format(source, path, commit))
        raise IssueRegisterError(
            '{0}: commit {1} is not in this repository. A commit written before '
            'the branch was rebased onto master no longer exists; re-point it at '
            'the commit that landed'.format(source, commit))


def _unverifiable(repo):
    """Why this checkout cannot answer, or ``None`` when it can."""
    if _git(repo, ['rev-parse', '--git-dir']) is None:
        return 'this is not a git checkout, or git is not installed'
    if _git(repo, ['rev-parse', '--is-shallow-repository']) == 'true':
        return 'a shallow clone holds too little history to check against'
    return None


def _git(repo, args, stdin=None):
    """Run ``git`` in ``repo`` and return its output, or ``None`` if it failed."""
    try:
        process = subprocess.Popen(
            ['git'] + args, cwd=repo,
            stdin=subprocess.PIPE if stdin is not None else None,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None
    output, _errors = process.communicate(
        stdin.encode('utf-8') if stdin is not None else None)
    if process.returncode != 0:
        return None
    return output.decode('utf-8', 'replace').strip()


class _IssueTableDirective(Directive):
    """Shared plumbing: get the register, note the dependencies, emit RST."""

    has_content = False

    def run(self):
        env = self.state.document.settings.env
        # Every issue file, so that changing one ``Status`` and rebuilding is
        # enough: Sphinx has no other way to know this page is derived from
        # documents it is not currently reading.
        for path in _register.paths:
            env.note_dependency(path)
        try:
            lines = self.build(_register)
        except IssueRegisterError as error:
            raise self.severe('issue register: {0}'.format(error))
        return parse_rst(self.state, lines)

    def build(self, register):
        raise NotImplementedError


class IssueRankDirective(_IssueTableDirective):
    """One group of the suggested order: the ranking body, as a table."""

    has_content = True

    def build(self, register):
        source = 'docs/issues/{0} line {1}'.format(INDEX_NAME, self.lineno)
        entries = issue_register.parse_rank_entries(list(self.content), source)
        rows = []
        for number, reason in entries:
            if number not in register.issues:
                raise IssueRegisterError(
                    '{0}: issue {1} is ranked but docs/issues/{1}-*.rst does '
                    'not exist'.format(source, number))
            issue = register.issues[number]
            rows.append([doc_link(issue), issue.severity, reason])
        return table(['ID', 'Severity', 'Why here'], rows, [8, 12, 80])


class IssueQueueDirective(_IssueTableDirective):
    """The ready queue: actionable status, nothing unfinished under it."""

    def build(self, register):
        rows = []
        for entry in register.ready:
            issue = entry.issue
            rows.append([
                doc_link(issue),
                issue.status,
                issue.severity,
                'needed' if issue.needs_decision else 'ruled',
                claim_cell(issue),
                entry.reason,
            ])
        if not rows:
            return ['Nothing is ready: every issue is either finished, being '
                    'worked on, or waiting for something below it.']
        return table(['ID', 'Status', 'Severity', 'Decision', 'Claimed',
                      'Why it is here'],
                     rows, [7, 11, 10, 11, 16, 70])


class IssueParkedDirective(_IssueTableDirective):
    """Everything the queue leaves out, and the one reason for each."""

    def build(self, register):
        rows = []
        for entry in register.parked:
            issue = entry.issue
            rows.append([
                doc_link(issue),
                issue.status,
                claim_cell(issue),
                entry.excluded_because,
            ])
        if not rows:
            return ['Nothing is left out: every issue in the register is in '
                    'the queue above.']
        return table(['ID', 'Status', 'Claimed', 'Not in the queue because'],
                     rows, [7, 13, 18, 62])


def claim_cell(issue):
    return issue.claimed.replace('\n', ' ') if issue.claimed else '--'


def doc_link(issue):
    """``:doc:`` reference by number; the title is one hop away either way."""
    return ':doc:`{0} <{1}>`'.format(issue.number, issue.docname)


def table(headers, rows, widths):
    """A ``list-table``: the only RST table that survives generated prose."""
    lines = [
        '.. list-table::',
        '   :header-rows: 1',
        '   :widths: {0}'.format(' '.join(str(width) for width in widths)),
        '',
    ]
    for row in [headers] + rows:
        for index, cell in enumerate(row):
            lines.append('   {0} {1}'.format('* -' if index == 0 else '  -',
                                             cell))
    lines.append('')
    return lines


def parse_rst(state, lines):
    """Render generated RST here, so ``:doc:`` and ``literals`` still work."""
    node = nodes.section()
    node.document = state.document
    content = StringList(lines, source='<issue register>')
    state.nested_parse(content, 0, node)
    return node.children


def setup(app):
    app.connect('builder-inited', load_register)
    app.add_directive('issue-rank', IssueRankDirective)
    app.add_directive('issue-queue', IssueQueueDirective)
    app.add_directive('issue-parked', IssueParkedDirective)
    return {'version': '1.0', 'parallel_read_safe': True,
            'parallel_write_safe': True}
