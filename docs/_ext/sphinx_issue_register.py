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

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import StringList
from sphinx.errors import ExtensionError
from sphinx.util import logging

import commit_pointers
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
        self.plan_paths = [os.path.join(srcdir, name)
                           for name in issue_register.PLANS]
        self.stages = self._read_stages(srcdir)

    def _read_stages(self, srcdir):
        """Each plan's ladder, in the order the plan puts it."""
        stages = []
        for name in issue_register.PLANS:
            source = 'docs/' + name
            with io.open(os.path.join(srcdir, name), encoding='utf-8') as handle:
                plan = issue_register.parse_stages(handle.read(), source)
            issue_register.check_stages(plan, source)
            stages.extend(plan)
        return stages

    def plan_stages(self, name):
        """One plan's stages, by file name."""
        return [stage for stage in self.stages if stage.source == 'docs/' + name]

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
        paths.extend(self.plan_paths)
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
                                                        _register.archive,
                                                        _register.stages))
    except IssueRegisterError as error:
        raise ExtensionError('issue register: {0}'.format(error))


def verify_commits(repo, references):
    """Fail the build when nobody can follow a commit the documentation names.

    A ``:Resolution:`` names the commit that fixed the issue and an archive
    entry names a commit that still holds a removed file, so both are promises
    about this repository's history. Both are written on a task branch whose
    commits are rewritten when it is rebased onto ``master``, and a pointer that
    died in that rebase reads exactly like a live one.

    The question is not whether the object is here. It is: the checkout that
    wrote the dead pointer holds the old commit, dangling, until ``git gc``
    takes it. The question is whether anything *reaches* it -- so a commit on a
    branch still in flight passes, a commit parked on a tag passes, and a commit
    on nothing at all fails. :mod:`commit_pointers` asks, in three ``git`` calls
    for the whole register.

    Where the history is not there to check -- no ``git``, a shallow clone, no
    ``master`` -- this reports that it skipped and passes: a checkout that
    cannot answer the question has not answered "no".
    """
    if not references:
        return
    git = commit_pointers.git_runner(repo)
    reason = commit_pointers.unverifiable(git)
    if reason:
        logger.info('issue register: not checking %d commit reference(s): %s',
                    len(references), reason)
        return
    pointers = commit_pointers.classify(commit_pointers.pointers(references),
                                        git)
    if pointers is None:
        logger.info('issue register: not checking %d commit reference(s): '
                    'git did not answer', len(references))
        return
    broken = [pointer for pointer in pointers if pointer.is_broken]
    in_flight = [pointer for pointer in pointers
                 if pointer.verdict == commit_pointers.PARKED]
    if in_flight:
        logger.info('issue register: %d commit reference(s) are not on %s yet, '
                    'but a branch or a tag holds them',
                    len(in_flight), commit_pointers.INTEGRATION)
    if broken:
        raise IssueRegisterError(_broken_message(broken))


def _broken_message(broken):
    """Every dead pointer at once, and the command that repairs them.

    One at a time would mean one build per pointer, and this project found
    eighteen of them in one go.
    """
    lines = ['{0} commit reference(s) point at nothing anybody can read:'
             .format(len(broken))]
    for pointer in broken:
        lines.append('  {0}: {1} -- {2}'.format(pointer.source, pointer.commit,
                                                _why(pointer)))
    lines.append(
        'A commit written before the branch was rebased onto master is on no '
        'branch afterwards. Run ``dev/repoint`` to see what each one became, '
        'and ``dev/repoint --write`` to re-point them. A commit that is '
        'deliberately off master needs a tag to hold it, as 062 does.')
    return '\n'.join(lines)


def _why(pointer):
    if pointer.verdict == commit_pointers.GONE:
        return 'git does not have this object'
    if pointer.verdict == commit_pointers.MISSING_PATH:
        return '``{0}`` is not in that commit'.format(pointer.path)
    return 'no branch and no tag reaches it'


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


class StageQueueDirective(_IssueTableDirective):
    """A plan's ladder: where it has got to, and which step is next.

    With an argument -- the plan's file name -- it is that plan's own table.
    Without one it is every plan at once, which is what :doc:`../issues/next`
    wants: the programme work beside the issue queue.
    """

    optional_arguments = 1

    def build(self, register):
        if self.arguments:
            name = self.arguments[0]
            if name not in issue_register.PLANS:
                raise IssueRegisterError(
                    'stage-queue: {0} is not a plan. The plans are {1}'
                    .format(name, ', '.join(issue_register.PLANS)))
            stages = register.plan_stages(name)
            headers = ['Stage', 'Status', 'What it is', 'Landed in']
            widths = [12, 10, 60, 18]
        else:
            stages = register.stages
            headers = ['Plan', 'Stage', 'Status', 'What it is', 'Landed in']
            widths = [20, 12, 10, 48, 18]
        rows = []
        for stage in stages:
            row = [stage.label, stage.status, stage.title,
                   ', '.join(issue_register.commits_in(stage.resolution)) or '--']
            if not self.arguments:
                plan = stage.source[len('docs/'):-len('.rst')]
                row.insert(0, ':doc:`{0} </{0}>`'.format(plan))
            rows.append(row)
        return table(headers, rows, widths)


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
    app.add_directive('stage-queue', StageQueueDirective)
    return {'version': '1.0', 'parallel_read_safe': True,
            'parallel_write_safe': True}
