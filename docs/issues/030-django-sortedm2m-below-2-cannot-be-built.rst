===================================================================
Issue 030: django-sortedm2m < 2.0.0 cannot be built by modern tools
===================================================================

:Status: Fixed
:Severity: Low
:Area: dependencies / build
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: (none)
:Blocks: 027 -- a constraint the lock must carry
    036 -- Stage 2 and Stages 4-11
:Related: (none)
:Decision: Be aware of it; act on nothing. The constraint is on the *builder*,
    not on the version -- sortedm2m 1.1.1-1.5.0 needs ``setuptools<60`` and an
    interpreter that still has ``distutils`` -- and every stage that pins one
    of them is built in an image old enough to provide both. Recorded beside
    ``django-sortedm2m==1.5.0`` in ``dev/Containerfile``, the only place the
    version is set, and in ``docs/upgrade-plan.rst`` 3b.3. The workaround the
    issue could only infer **is now verified**, on the two interpreters that
    matter: see "Verified since" below. Nothing installed changed.
:Resolution: 679d96d records the build-tool bound beside the pin, and the
    measurements that turned the inferred workaround into a verified one

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

What was recorded, and where
============================

Beside ``django-sortedm2m==1.5.0`` in ``dev/Containerfile``, which is the only
place the version is set -- ``requirements/production.txt`` does not mention
the package at all, which is issue 027 -- and in ``docs/upgrade-plan.rst``
3b.3. The comment says what the pin needs from whatever builds it, rather than
only what version it is. No pin changed.

Not fully verified when this was filed
======================================

The failure is confirmed. The workaround is inferred: testing it needs
``setuptools<60``, which will not import on Python 3.12+ because ``distutils``
is gone, and no older interpreter was available when this was investigated.

Verified since
==============

One was available after all -- ``nix-shell -p python311`` -- so the inference
above was measured instead of carried forward. On Python 3.11.15, installing
``django-sortedm2m==1.5.0`` from the sdist:

===================== ==========================================
setuptools in the env result
===================== ==========================================
59.8.0                builds, wheel produced, installs
83.0.0                fails -- ``AttributeError:
                      'UltraMagicString' object has no attribute
                      'endswith'``, at
                      ``_core_metadata.py`` line 221
===================== ==========================================

Same interpreter, same sdist, same pip: **the boundary is setuptools, not the
Python version.** ``distutils`` matters only because setuptools old enough to
work needs it.

And the container the upgrade plan actually assumes for those stages was
checked rather than assumed: ``docker.io/library/python:3.7-alpine`` ships
Python 3.7.17 and **setuptools 57.5.0**, and ``pip install
django-sortedm2m==1.5.0`` in it succeeds. So does the Python 2.7 image this
project uses today. The plan's "period-appropriate image" holds for both.

One detail worth carrying, because it decides which setuptools is the one that
counts: these sdists have no ``pyproject.toml``, so pip does **not** build them
in an isolated environment. The setuptools that runs ``setup.py`` is whatever
is installed in the target environment -- which is why the failure follows the
environment rather than the tool version somebody thinks they are using.

What 027 has to carry
=====================

No version bound at all -- this one constrains the *builder*, and a lock file
has nowhere to say that. What the lock can do is make the requirement visible:
Stages 2 and 4-11 pin ``django-sortedm2m`` between 1.1.1 and 1.5.0, and each
of those stages has to be built somewhere with ``setuptools<60``. If 027
adopts ``uv pip compile``, note that the constraint is on the machine doing
the build, not on anything the resolver can select. The way out, if a stage
ever has to be built on a current toolchain, is sortedm2m 2.0.0 -- the first
release with a wheel, and a Django 1.11 floor, so not available before
Stage 9.

See also
========

``docs/upgrade-plan.rst`` Part 3b.3.
