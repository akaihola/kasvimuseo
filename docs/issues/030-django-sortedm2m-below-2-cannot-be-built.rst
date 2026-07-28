==================================================================
Issue 030: django-sortedm2m < 2.0.0 cannot be built by modern tools
==================================================================

:Status: Open
:Severity: Low
:Area: dependencies / build
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Decision: undecided
:Resolution: (none yet)

Problem
=======

``django-sortedm2m`` releases 1.1.1 through 1.5.0 are **sdist-only** -- no
wheels were ever published -- so every installation builds them from source.
Their ``setup.py`` wraps ``long_description`` in a custom ``UltraMagicString``
class, and current setuptools does::

    File "setuptools/_core_metadata.py", line 221, in write_pkg_file
        if not long_description.endswith("\n"):
    AttributeError: 'UltraMagicString' object has no attribute 'endswith'

Wheels first appear at 2.0.0:

=================== ===========================
version             distributions on PyPI
=================== ===========================
1.1.1 ... 1.5.0     sdist only
**2.0.0**           sdist + wheel
3.0.0 ...           wheel
=================== ===========================

This affects the upgrade stages that need sortedm2m 1.1.1-1.5.0 to match their
photologue: Stage 2, and Stages 4 through 11.

Impact
======

Low, and only for rebuilds. The version currently installed --
``django-sortedm2m==1.5.0``, put there by ``dev/Containerfile`` -- builds fine
inside the Python 2.7 container, which has an old setuptools. Nothing is broken
today.

It becomes a problem when someone tries to rebuild an early stage on a current
machine and gets a build failure with no obvious connection to the version they
asked for.

Options
=======

Build the early stages inside a period-appropriate image: an old ``setuptools``
(< 60) and an interpreter that still has ``distutils`` (< 3.12). That is
already true of the Python 2.7 container and stays true of a Python 3.7 one, so
in practice this is a constraint to be *aware of* rather than to act on --
provided the staged containers are period-appropriate, which the upgrade plan
assumes.

Worth recording so that a future build failure is recognised rather than
debugged from scratch.

Not fully verified
==================

The failure is confirmed. The workaround is inferred: testing it needs
``setuptools<60``, which will not import on Python 3.12+ because ``distutils``
is gone, and no older interpreter was available when this was investigated.

See also
========

``docs/upgrade-plan.rst`` Part 3b.3.
