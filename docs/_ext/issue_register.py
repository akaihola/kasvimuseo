# -*- coding: utf-8 -*-
"""Read the issue register's metadata, and work out what is ready to do.

The issue files under ``docs/issues/`` already carry every fact this needs, in
their reStructuredText docinfo block: ``Status``, ``Severity``, ``Depends on``,
``Decision`` and the optional ``Claimed``. The order to do them in is the one
human judgement in the register, and it is recorded next to the prose that
argues for it, in ``docs/issues/index.rst`` ``issue-rank`` directives.

Nothing here imports Sphinx, and nothing here is Python 3 only: the Sphinx
extension in ``sphinx_issue_register.py`` drives it on the host's Python 3, and
``kasvimuseo/tests/test_issue_register.py`` drives it inside the application's
Python 2.7 container. See ``docs/issues/README.rst`` for the fields themselves.
"""

from __future__ import unicode_literals

import io
import os
import re

#: Every ``Status`` value ``docs/issues/README.rst`` defines.
STATUSES = ('Open', 'Accepted', 'In progress', 'Fixed', 'Rejected', 'Deferred')

#: The two that mean "somebody could pick this up now".
ACTIONABLE = ('Open', 'Accepted')

SEVERITIES = ('High', 'Medium', 'Low')

#: The fields every issue file carries. ``Claimed`` is the one optional field.
REQUIRED_FIELDS = ('Status', 'Severity', 'Area', 'Reported', 'Source',
                   'Evidence', 'Depends on', 'Blocks', 'Related', 'Decision',
                   'Resolution')
OPTIONAL_FIELDS = ('Claimed',)

#: ``Decision`` until the maintainer rules on it.
UNDECIDED = 'undecided'

# Underscores appear in the slug when the identifier does: 012 is named after
# ``public_planted``.
ISSUE_FILE_RE = re.compile(r'^(\d{3})-[a-z0-9_.-]+\.rst$')
FIELD_RE = re.compile(r'^:([A-Za-z][A-Za-z ]*):(?:[ \t]+(.*))?$')
NONE_RE = re.compile(r'^\(none[^)]*\)')
LEADING_IDS_RE = re.compile(r'^\s*(\d{3}(?:\s*,\s*\d{3})*)')
RANK_ENTRY_RE = re.compile(r'^(\d{3}):[ \t]*(.*)$')
RANK_DIRECTIVE_RE = re.compile(r'^([ \t]*)\.\.[ \t]+issue-rank::[ \t]*$')


class IssueRegisterError(Exception):
    """A malformed issue file, or a ranking that does not match the files.

    Raised rather than warned: a register that cannot be read is not a page
    with a typo in it, and both callers stop on it.
    """


class Issue(object):
    """One ``docs/issues/NNN-slug.rst``, as its docinfo block describes it."""

    def __init__(self, number, docname, title, fields):
        self.number = number
        self.docname = docname
        self.title = title
        self.fields = fields
        self.status = fields['Status']
        self.severity = fields['Severity']
        self.decision = fields['Decision']
        self.claimed = fields.get('Claimed')
        self.depends_on = _referenced_ids(fields['Depends on'])

    @property
    def is_actionable(self):
        return self.status in ACTIONABLE

    @property
    def needs_decision(self):
        return self.decision.strip().lower().startswith(UNDECIDED)

    def __repr__(self):
        return str('<Issue {0} {1}>').format(self.number, self.status)


def parse_docinfo(text):
    """Return the docinfo field list at the top of ``text``, in file order.

    A field runs until the next ``:Field:`` line or the blank line that ends
    the block; continuation lines are indented and are joined with newlines,
    because ``Depends on`` uses one line per referenced issue.
    """
    fields = []
    current = None
    started = False
    for line in text.split('\n'):
        match = FIELD_RE.match(line)
        if match:
            started = True
            current = [match.group(1), (match.group(2) or '').strip()]
            fields.append(current)
            continue
        if not started:
            continue
        if not line.strip():
            break
        if current is not None and line[:1].isspace():
            current[1] = (current[1] + '\n' + line.strip()).strip()
            continue
        break
    return fields


def parse_issue(path, text=None):
    """Read one issue file into an :class:`Issue`, or raise on a bad one."""
    name = os.path.basename(path)
    match = ISSUE_FILE_RE.match(name)
    if not match:
        raise IssueRegisterError(
            '{0}: an issue file is named NNN-short-slug.rst'.format(path))
    number = match.group(1)
    if text is None:
        with io.open(path, encoding='utf-8') as handle:
            text = handle.read()

    fields = {}
    for field, value in parse_docinfo(text):
        if field in fields:
            raise IssueRegisterError(
                '{0}: ``:{1}:`` is given twice'.format(path, field))
        if field not in REQUIRED_FIELDS and field not in OPTIONAL_FIELDS:
            raise IssueRegisterError(
                '{0}: unknown field ``:{1}:``. docs/issues/README.rst defines '
                '{2} and the optional {3}'
                .format(path, field, ', '.join(REQUIRED_FIELDS),
                        ', '.join(OPTIONAL_FIELDS)))
        fields[field] = value

    missing = [f for f in REQUIRED_FIELDS if f not in fields]
    if missing:
        raise IssueRegisterError(
            '{0}: no {1} field. docs/issues/README.rst says every issue '
            'carries one, so a missing edge is a statement rather than an '
            'omission'
            .format(path, ' or '.join('``:{0}:``'.format(f) for f in missing)))

    _check_value(path, fields, 'Status', STATUSES)
    _check_value(path, fields, 'Severity', SEVERITIES)
    for field in ('Depends on', 'Decision') + OPTIONAL_FIELDS:
        if field in fields and not fields[field].strip():
            raise IssueRegisterError(
                '{0}: ``:{1}:`` is empty. Write ``(none)`` if that is what it '
                'means'.format(path, field))

    return Issue(number, name[:-len('.rst')], _title(text), fields)


def load_issues(issues_dir):
    """Read every ``NNN-slug.rst`` in ``issues_dir``, keyed by issue number."""
    issues = {}
    for name in sorted(os.listdir(issues_dir)):
        if not ISSUE_FILE_RE.match(name):
            continue
        issue = parse_issue(os.path.join(issues_dir, name))
        if issue.number in issues:
            raise IssueRegisterError(
                '{0}: two issue files are numbered {1}'
                .format(issues_dir, issue.number))
        issues[issue.number] = issue
    if not issues:
        raise IssueRegisterError(
            '{0}: no issue files found'.format(issues_dir))
    return issues


def parse_rank_entries(lines, source='<rank>'):
    """Parse one ``issue-rank`` body into ``[(number, reason)]``.

    Each entry starts at column zero with ``NNN: why``; the reason wraps onto
    indented continuation lines, which are rewrapped into one paragraph.
    """
    entries = []
    for line in lines:
        if not line.strip():
            continue
        match = RANK_ENTRY_RE.match(line)
        if match:
            entries.append([match.group(1), match.group(2).strip()])
            continue
        if line[:1].isspace() and entries:
            entries[-1][1] = (entries[-1][1] + ' ' + line.strip()).strip()
            continue
        raise IssueRegisterError(
            '{0}: cannot read ``{1}`` as a ranking entry. Each one starts '
            '``NNN: why this is here``, with the reason wrapped onto indented '
            'lines'.format(source, line.strip()))
    for number, reason in entries:
        if not reason:
            raise IssueRegisterError(
                '{0}: ranking entry {1} says nothing. The reason is what the '
                'queue shows'.format(source, number))
    return entries


def parse_ranking(index_text, source='index.rst'):
    """Collect every ``issue-rank`` block in ``index_text``, in page order."""
    entries = []
    lines = index_text.split('\n')
    position = 0
    while position < len(lines):
        match = RANK_DIRECTIVE_RE.match(lines[position])
        if not match:
            position += 1
            continue
        indent = len(match.group(1))
        body = []
        position += 1
        while position < len(lines):
            line = lines[position]
            if line.strip() and len(line) - len(line.lstrip()) <= indent:
                break
            body.append(line)
            position += 1
        entries.extend(parse_rank_entries(_dedent(body), source))
    return entries


def check_ranking(issues, ranking, source='docs/issues/index.rst'):
    """Enforce ``index.rst``'s promise that every issue appears exactly once."""
    seen = []
    for number, _reason in ranking:
        if number in seen:
            raise IssueRegisterError(
                '{0}: issue {1} is ranked twice. "Every issue appears exactly '
                'once" -- delete one of them'.format(source, number))
        if number not in issues:
            raise IssueRegisterError(
                '{0}: issue {1} is ranked but docs/issues/{1}-*.rst does not '
                'exist'.format(source, number))
        seen.append(number)
    unranked = sorted(set(issues) - set(seen))
    if unranked:
        raise IssueRegisterError(
            '{0}: {1} not ranked. Every issue appears exactly once in '
            '"Suggested order of implementation": add {2} to the '
            '``issue-rank`` block of the group it belongs in'
            .format(source,
                    ', '.join('issue ' + number for number in unranked),
                    'it' if len(unranked) == 1 else 'them'))


class QueueEntry(object):
    """One row of either generated table: an issue, its rank and its reason."""

    def __init__(self, issue, reason, blockers):
        self.issue = issue
        self.reason = reason
        #: ``[(number, status)]`` of the ``Depends on`` issues not yet fixed.
        self.blockers = blockers

    @property
    def excluded_because(self):
        """Why this is not in the queue, or ``None`` if it is."""
        if self.issue.status not in ACTIONABLE:
            return 'Status is ``{0}``'.format(self.issue.status)
        if self.blockers:
            return 'waits for {0}'.format(', '.join(
                '{0} (``{1}``)'.format(number, status)
                for number, status in self.blockers))
        return None


def build_queue(issues, ranking):
    """Split the ranked issues into (ready now, everything else).

    Ready means the two things a picker cares about: the status says somebody
    could start it, and nothing it depends on is still unfinished.
    """
    ready = []
    parked = []
    for number, reason in ranking:
        issue = issues[number]
        blockers = [(dep, issues[dep].status) for dep in issue.depends_on
                    if dep in issues and issues[dep].status != 'Fixed']
        entry = QueueEntry(issue, reason, blockers)
        (parked if entry.excluded_because else ready).append(entry)
    return ready, parked


def _check_value(path, fields, field, allowed):
    if fields[field] not in allowed:
        raise IssueRegisterError(
            '{0}: ``:{1}: {2}`` is not one of {3}'
            .format(path, field, fields[field],
                    ', '.join('``{0}``'.format(value) for value in allowed)))


def _referenced_ids(value):
    """The issue numbers a ``Depends on`` field names, in order.

    One dependency per line, each ``NNN[, NNN...] -- why``, so take the numbers
    each line starts with and ignore the prose.
    """
    if NONE_RE.match(value.strip()):
        return []
    numbers = []
    for line in value.split('\n'):
        match = LEADING_IDS_RE.match(line)
        if not match:
            continue
        for number in match.group(1).split(','):
            number = number.strip()
            if number not in numbers:
                numbers.append(number)
    return numbers


def _title(text):
    """The issue's title: the line between the two ``===`` rules."""
    lines = text.split('\n')
    for index, line in enumerate(lines[:-1]):
        if set(line.strip()) == set('=') and line.strip():
            return lines[index + 1].strip()
    return ''


def _dedent(lines):
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    width = min(indents) if indents else 0
    return [line[width:] if line.strip() else '' for line in lines]
