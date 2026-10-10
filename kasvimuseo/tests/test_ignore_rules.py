"""The committed ignore rules keep private local state out of Git (task 4).

A fresh clone has no ``.git/info/exclude`` and no global excludes file, so
``.gitignore`` alone must stop ``git add`` from picking up a developer's
``.dev`` state -- a directory or a symlink to one -- the agent and editor
configuration under ``.claude/``, and the machine-specific settings modules.
``.containerignore`` must keep the same files out of the Podman build
context, without hiding a file the production ``Dockerfile`` copies.

The Git checks build a disposable repository under ``tmp_path`` with the
tracked ``.gitignore`` and nothing else, and point Git away from every other
exclusion source. The container checks apply ``.containerignore`` with the
same rules Podman and Docker use: a pattern is cleaned of its leading and
trailing slashes and excludes a path when it matches the path or one of its
parent directories.
"""

import os
import re
import shutil
import subprocess

import pytest

# From this file, not from the application: these checks need no Django,
# so they also run on a host with nothing but pytest and git.
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Private local state that a contributor may have in a working checkout.
PRIVATE = [
    '.claude/settings.json',
    '.claude/settings.local.json',
    '.claude/worktrees/task/README.rst',
    '.mcp.json',
    '.vscode/settings.json',
    '.idea/workspace.xml',
    '.serena/project.yml',
    '.codegraph/index.db',
    '.worktrees/task/README.rst',
    '.env',
    '.env.production',
    'ylaneenkasvit/local_settings.py',
    'ylaneenkasvit/local_settings.staging.py',
    'ylaneenkasvit/kajala_settings.py',
    'ansible/hosts',
    'ansible.cfg',
    'backups/production.sql',
    'backups/production.sql.gz',
    'backups/production.dump',
]
# The same, as it appears in the ``.dev`` state directory.
DEV_STATE = '.dev/docs/html/index.html'

# Public files that must stay trackable. One from each directory the ignore
# rules touch, and the shared agent memory, which lives beside ``.claude/``.
PUBLIC = [
    '.agents/memory/MEMORY.md',
    '.containerignore',
    '.github/workflows/tests.yml',
    'AGENTS.md',
    'README.rst',
    'dev/Containerfile',
    'dev/kasvimuseo',
    'docs/conf.py',
    'kasvimuseo/tests/test_ignore_rules.py',
    'requirements/dev.txt',
    'ylaneenkasvit/common_settings.py',
    'ylaneenkasvit/test_settings.py',
]

# What ``Dockerfile`` copies into the production image.
COPIED = [
    'MANIFEST.in',
    'setup.py',
    'jqm/README.rst',
    'kasvimuseo/migrations/0001_initial.py',
    'requirements/production.txt',
    'ylaneenkasvit/common_settings.py',
]


def plant(root, relative, content=''):
    path = os.path.join(root, relative)
    directory = os.path.dirname(path)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    with open(path, 'w') as handle:
        handle.write(content)
    return path


def git(repo, *args):
    """Run Git in ``repo`` with no exclusion source but the checkout's own.

    Returns ``(exit status, output)``.
    """
    env = dict(os.environ,
               HOME=repo, GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_SYSTEM=os.devnull, GIT_CONFIG_NOSYSTEM='1')
    process = subprocess.run(
        ['git', '-c', 'core.excludesFile=' + os.devnull] + list(args),
        cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False)
    return process.returncode, process.stdout.decode('utf-8', 'replace')


@pytest.fixture(params=['directory', 'symlink'])
def checkout(request, tmp_path):
    """A disposable repository with the tracked ``.gitignore`` only.

    ``.dev`` is a directory in one run and a symlink to a directory outside
    the checkout in the other, which is what the tracked ``/.dev/`` pattern
    used to miss.
    """
    if shutil.which('git') is None:
        pytest.skip('git is not installed')
    repo = str(tmp_path / 'checkout')
    os.mkdir(repo)
    status, output = git(repo, 'init', '-q')
    assert status == 0, output
    # A fresh clone has an empty one; the developer's own must not help.
    with open(os.path.join(repo, '.git', 'info', 'exclude'), 'w'):
        pass
    shutil.copy(os.path.join(REPO_ROOT, '.gitignore'), repo)
    for relative in PUBLIC + PRIVATE:
        plant(repo, relative)
    if request.param == 'directory':
        plant(repo, DEV_STATE)
    else:
        elsewhere = str(tmp_path / 'elsewhere')
        plant(elsewhere, DEV_STATE[len('.dev/'):])
        os.symlink(elsewhere, os.path.join(repo, '.dev'))
    return repo


def ignored(repo, relative):
    status, _ = git(repo, 'check-ignore', '-q', '--', relative)
    return status == 0


def test_check_ignore_accepts_every_private_path(checkout):
    # Git does not look through a symlink, so what matters for one is the
    # link itself; a directory is checked by what is inside it.
    dev = DEV_STATE if os.path.isdir(os.path.join(checkout, '.dev')) \
        and not os.path.islink(os.path.join(checkout, '.dev')) else '.dev'
    missed = [relative for relative in PRIVATE + [dev]
              if not ignored(checkout, relative)]
    assert missed == []


def test_check_ignore_leaves_the_public_files_alone(checkout):
    hidden = [relative for relative in PUBLIC + ['.gitignore']
              if ignored(checkout, relative)]
    assert hidden == []


def test_add_dry_run_selects_only_the_public_files(checkout):
    status, output = git(checkout, 'add', '--dry-run', '--all', '--', '.')
    assert status == 0, output
    added = sorted(re.findall(r"^add '(.*)'$", output, re.MULTILINE))
    assert added == sorted(PUBLIC + ['.gitignore'])


# -- The container build context --------------------------------------------

def container_patterns():
    with open(os.path.join(REPO_ROOT, '.containerignore')) as handle:
        lines = [line.strip() for line in handle]
    return [line for line in lines if line and not line.startswith('#')]


def pattern_regex(pattern):
    """Translate one ``.containerignore`` pattern into a regular expression.

    Podman and Docker clean the pattern first, so ``.dev/`` and ``/.dev``
    both mean ``.dev``. ``**`` crosses directories; ``*`` and ``?`` do not,
    so ``*.sql`` is a root-level rule and ``**/*.sql`` is the one that
    reaches a subdirectory.
    """
    parts = []
    for piece in re.split(r'(\*\*/?|\*|\?)', pattern.strip('/')):
        if piece in ('**/', '**'):
            parts.append('(.*/)?' if piece == '**/' else '.*')
        elif piece == '*':
            parts.append('[^/]*')
        elif piece == '?':
            parts.append('[^/]')
        else:
            parts.append(re.escape(piece))
    return re.compile('^' + ''.join(parts) + '$')


def excluded_from_context(relative, patterns=None):
    """True when the build context leaves ``relative`` out.

    A pattern excludes a path when it matches the path or any directory
    above it: ``.claude/`` keeps ``.claude/settings.json`` out.
    """
    regexes = [pattern_regex(p) for p in patterns or container_patterns()]
    candidates = []
    path = relative
    while path:
        candidates.append(path)
        path = os.path.dirname(path)
    return any(regex.match(candidate)
               for regex in regexes for candidate in candidates)


def test_the_pattern_rules_match_what_podman_does():
    assert excluded_from_context('.dev/docs/index.html', ['.dev/'])
    assert excluded_from_context('.dev', ['.dev/'])
    assert excluded_from_context('b.pyc', ['*.pyc'])
    assert not excluded_from_context('a/b.pyc', ['*.pyc'])
    assert excluded_from_context('a/b.pyc', ['**/*.pyc'])
    assert excluded_from_context('a/.claude/x', ['**/.claude/'])
    assert not excluded_from_context('a/b.py', ['*.py'])
    assert not excluded_from_context('dev/Containerfile', ['.dev'])


def test_the_build_context_excludes_every_private_path():
    kept = [relative for relative in PRIVATE + ['.dev', DEV_STATE]
            if not excluded_from_context(relative)]
    assert kept == []


def test_the_build_context_keeps_what_the_dockerfile_copies():
    lost = [relative for relative in COPIED if excluded_from_context(relative)]
    assert lost == []
