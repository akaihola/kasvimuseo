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

#: One ``docs/archive.rst`` bullet: ``* ``path`` @ ``commit`` -- why it went``.
ARCHIVE_ENTRY_RE = re.compile(
    r'^\*[ \t]+``([^`]+)``[ \t]+@[ \t]+``([0-9a-fA-F]+)``[ \t]+--[ \t]*(.+)$')
#: A bullet that opens with a literal is meant to be one, whatever it says.
ARCHIVE_BULLET_RE = re.compile(r'^\*[ \t]+``')

#: A commit named in prose: a hex run, not part of a longer word and not inside
#: a path. ``git`` accepts any unambiguous prefix, so the length is not fixed at
#: seven. A backtick may open it: ``` ``a58a697`` ``` is how this documentation
#: usually writes one, and a pointer the check cannot see is a pointer nothing
#: checks.
COMMIT_RE = re.compile(r'(?<![0-9A-Za-z_/-])([0-9a-f]{7,40})(?![0-9A-Za-z])')

#: The plans, whose stages are a second queue beside the issues. Named here
#: rather than discovered: a plan is a document somebody decided to run, and
#: there are two of them.
PLANS = ('upgrade-plan.rst', 'test-coverage-plan.rst')

#: What a stage's ``Status`` may say. There is no ``In progress``: a stage is
#: not claimed, it is next, and ``docs/issues/NNN``'s ``Claimed`` is where the
#: branch doing it says so.
STAGE_STATUSES = ('Done', 'Next', 'Planned')

#: ``Stage 3 -- Django 1.5.12 -> 1.6.11``, ``P1 -- Public-visibility logic``.
STAGE_HEADING_RE = re.compile(
    r'^(Stage|Step|P)[ \t]*(\d+)[ \t]*(?:[-–—]+[ \t]*)?(.*)$')
#: A section underline: one punctuation character, repeated, and nothing else.
#: A simple-table rule has spaces in it, which is what keeps its header row out.
UNDERLINE_RE = re.compile(r'^([-=~^"*+#`\'])\1{2,}$')


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


def check_graph(issues):
    """Enforce that ``Depends on`` and ``Blocks`` name real issues, both ways.

    ``docs/issues/README.rst`` says the two are kept consistent in both
    directions, so that the graph can be read from either file. Nothing checked
    it until this did, and a dependency naming an issue that does not exist was
    worse than unchecked: :func:`build_queue` skipped it, so a typo in a
    ``Depends on`` line read as "ready now".
    """
    for number in sorted(issues):
        issue = issues[number]
        path = 'docs/issues/{0}.rst'.format(issue.docname)
        for field, mirror in (('Depends on', 'Blocks'),
                              ('Blocks', 'Depends on')):
            for other in _referenced_ids(issue.fields[field]):
                if other == number:
                    raise IssueRegisterError(
                        '{0}: ``:{1}:`` names {2} itself'
                        .format(path, field, number))
                if other not in issues:
                    raise IssueRegisterError(
                        '{0}: ``:{1}:`` names issue {2}, which has no file. '
                        'Either docs/issues/{2}-*.rst is missing or the number '
                        'is a typo -- an unreadable edge is dropped from the '
                        'queue, so this cannot be left as it is'
                        .format(path, field, other))
                if number not in _referenced_ids(issues[other].fields[mirror]):
                    raise IssueRegisterError(
                        '{0}: ``:{1}:`` names {2}, but docs/issues/{3}.rst does '
                        'not name {4} in its ``:{5}:``. The two are kept '
                        'consistent in both directions, so the graph can be '
                        'read from either file: add {4} there, or drop it here'
                        .format(path, field, other, issues[other].docname,
                                number, mirror))


def parse_archive(text, source='docs/archive.rst'):
    """Read the archive page into ``[(path, commit, why it went)]``.

    One bullet per removed document, ``* ``path`` @ ``commit`` -- why``, with
    the prose wrapping onto indented lines. The format is fixed because
    :func:`commit_references` hands every pointer to ``git``; it is written
    down in ``docs/issues/README.rst``.
    """
    entries = []
    for number, line in enumerate(text.split('\n'), start=1):
        if entries and line[:1].isspace() and line.strip():
            entries[-1][2] = (entries[-1][2] + ' ' + line.strip()).strip()
            continue
        if not ARCHIVE_BULLET_RE.match(line):
            continue
        match = ARCHIVE_ENTRY_RE.match(line)
        if not match:
            raise IssueRegisterError(
                '{0} line {1}: cannot read this as an archive entry. Each one '
                'is ``* ``path`` @ ``commit`` -- why it went``, with the commit '
                'already on master: {2}'.format(source, number, line.strip()))
        entries.append([match.group(1), match.group(2), match.group(3).strip()])
    return [tuple(entry) for entry in entries]


class Stage(object):
    """One step of a plan, as the field list under its heading describes it."""

    def __init__(self, label, title, fields, source, lineno):
        self.label = label
        self.title = title
        self.fields = fields
        self.source = source
        self.lineno = lineno
        self.status = fields['Status']
        self.resolution = fields.get('Resolution', '')

    @property
    def is_done(self):
        return self.status == 'Done'

    def __repr__(self):
        return str('<Stage {0} {1}>').format(self.label, self.status)


def parse_stages(text, source):
    """Read one plan's stages, in the order the document puts them.

    A stage is a section whose first content is a field list carrying
    ``Status``. The heading normally names it -- ``Stage 4``, ``P1`` -- and
    ``:Stage:`` says so explicitly where the heading does not.

    The prose around each stage stays what it always was: the argument for
    doing it that way, and the record of what it cost. This reads the one line
    that says where the work has got to, so that :doc:`../issues/next` can show
    it without anybody maintaining a second copy of it.
    """
    stages = []
    lines = text.split('\n')
    for index in range(len(lines) - 1):
        heading = lines[index].strip()
        if not heading or not UNDERLINE_RE.match(lines[index + 1].strip()):
            continue
        if len(lines[index + 1].strip()) < len(heading):
            continue
        fields = _fields_after(lines, index + 2)
        if 'Status' not in fields:
            continue
        lineno = index + 1
        label, title = _stage_label(heading, fields, source, lineno)
        _check_value('{0} line {1}'.format(source, lineno), fields, 'Status',
                     STAGE_STATUSES)
        if fields['Status'] == 'Done' and not fields.get('Resolution', '').strip():
            raise IssueRegisterError(
                '{0} line {1}: {2} is ``Done`` with no ``:Resolution:``. Name '
                'the commit that landed it, or the issues that did'
                .format(source, lineno, label))
        stages.append(Stage(label, title, fields, source, lineno))
    if not stages:
        raise IssueRegisterError(
            '{0}: no stages. A plan says where it has got to in a ``:Status:`` '
            'field under each stage heading, one of {1}'
            .format(source, ', '.join('``{0}``'.format(value)
                                      for value in STAGE_STATUSES)))
    return stages


def check_stages(stages, source):
    """A ladder is climbed in order, so its statuses have to read like one.

    ``Done`` stages first, then at most one ``Next``, then ``Planned``. A plan
    with work left says which piece is next -- that is the whole point of
    reading it -- and a plan with none left says so by having no ``Next`` at
    all, which is how a finished plan stops asking to be read.
    """
    remaining = [stage for stage in stages if not stage.is_done]
    for stage in stages[len(stages) - len(remaining):]:
        if stage.is_done:
            raise IssueRegisterError(
                '{0} line {1}: {2} is ``Done`` but a stage above it is not. '
                'A stage that was taken out of order is still out of order in '
                'the plan: move it, or say in its prose why it could jump'
                .format(source, stage.lineno, stage.label))
    nexts = [stage for stage in stages if stage.status == 'Next']
    if len(nexts) > 1:
        raise IssueRegisterError(
            '{0}: {1} are both ``Next``. One of them is'
            .format(source, ' and '.join(stage.label for stage in nexts)))
    if remaining and not nexts:
        raise IssueRegisterError(
            '{0} line {1}: nothing is ``Next``, but {2} is not done. Mark the '
            'one to do next, so that the queue can name it'
            .format(source, remaining[0].lineno, remaining[0].label))
    if nexts and nexts[0] is not remaining[0]:
        raise IssueRegisterError(
            '{0} line {1}: {2} is ``Next``, but {3} above it is not done '
            'either'.format(source, nexts[0].lineno, nexts[0].label,
                            remaining[0].label))


def _fields_after(lines, start):
    """The field list that opens a section, or ``{}`` if it does not."""
    while start < len(lines) and not lines[start].strip():
        start += 1
    fields = {}
    current = None
    for line in lines[start:]:
        match = FIELD_RE.match(line)
        if match:
            current = match.group(1)
            fields[current] = (match.group(2) or '').strip()
            continue
        if not line.strip():
            break
        if current is not None and line[:1].isspace():
            fields[current] = (fields[current] + ' ' + line.strip()).strip()
            continue
        break
    return fields


def _stage_label(heading, fields, source, lineno):
    """What to call this stage, and what the heading says it is."""
    match = STAGE_HEADING_RE.match(heading)
    if 'Stage' in fields:
        return fields['Stage'], heading
    if not match:
        raise IssueRegisterError(
            '{0} line {1}: ``{2}`` carries a stage ``:Status:`` but its '
            'heading does not name a stage. Add ``:Stage:`` saying what to '
            'call it'.format(source, lineno, heading))
    prefix, number, title = match.groups()
    label = '{0} {1}'.format(prefix, number) if prefix != 'P' else prefix + number
    return label, title.strip() or heading


def commit_references(issues, archive=(), stages=()):
    """Every commit the documentation points at, as ``[(source, commit, path)]``.

    ``path`` is the file the commit has to contain -- the archive's whole
    purpose -- or ``None`` when only the commit itself is claimed to exist,
    which is what a ``:Resolution:`` claims.

    A ``:Resolution:`` names its commits in prose, so they are picked out by
    shape: a bare hex run of at least seven characters with both a digit and a
    letter in it. That last rule is what keeps ``max-age=31536000`` in issue 060
    out, and it is deliberately a shape rather than a syntax -- the fields were
    written for people first, and a commit this misses is unchecked rather than
    wrongly reported.
    """
    references = []
    for number in sorted(issues):
        issue = issues[number]
        source = 'docs/issues/{0}.rst'.format(issue.docname)
        for commit in commits_in(issue.fields['Resolution']):
            references.append((source + ' ``:Resolution:``', commit, None))
    for path, commit, _why in archive:
        references.append(('docs/archive.rst', commit, path))
    for stage in stages:
        for commit in commits_in(stage.resolution):
            references.append(
                ('{0} {1} ``:Resolution:``'.format(stage.source, stage.label),
                 commit, None))
    return references


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


def commits_in(value):
    """The commits a prose field names, deduplicated and in order."""
    commits = []
    for candidate in COMMIT_RE.findall(value):
        if not any(char.isdigit() for char in candidate):
            continue
        if not any(char in 'abcdef' for char in candidate):
            continue
        if candidate not in commits:
            commits.append(candidate)
    return commits


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
