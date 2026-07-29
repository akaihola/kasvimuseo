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

import issue_register
from issue_register import IssueRegisterError

INDEX_NAME = 'index.rst'

#: Read once per build, in ``builder-inited``, and used by every directive.
#: Deliberately not on ``env``: it is derived from files Sphinx already tracks
#: as dependencies, so there is nothing to carry over to the next build.
_register = None


class Register(object):
    """Everything the directives need, read once per build."""

    def __init__(self, issues_dir):
        self.issues_dir = issues_dir
        self.issues = issue_register.load_issues(issues_dir)
        self.index_path = os.path.join(issues_dir, INDEX_NAME)
        with io.open(self.index_path, encoding='utf-8') as handle:
            self.ranking = issue_register.parse_ranking(
                handle.read(), 'docs/issues/' + INDEX_NAME)
        issue_register.check_ranking(self.issues, self.ranking,
                                     'docs/issues/' + INDEX_NAME)
        self.ready, self.parked = issue_register.build_queue(self.issues,
                                                             self.ranking)

    @property
    def paths(self):
        """Every file the generated tables are derived from."""
        return [self.index_path] + [
            os.path.join(self.issues_dir, issue.docname + '.rst')
            for issue in self.issues.values()]


def load_register(app):
    """Read the register, turning its own errors into build failures."""
    global _register
    try:
        _register = Register(os.path.join(app.srcdir, 'issues'))
    except IssueRegisterError as error:
        raise ExtensionError('issue register: {0}'.format(error))


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
