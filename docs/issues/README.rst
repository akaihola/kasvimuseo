======
Issues
======

Known problems, kept in the repository so they travel with the code and can be
reviewed in a diff. One file per issue, named ``NNN-short-slug.rst``, numbered
in the order they were filed and never reused.

The layout follows the decision-record convention used elsewhere in these
projects (``docs/adr/NNN-slug.md``): a numbered file, a title, and a metadata
block at the top whose ``Status`` field is the thing you actually track. The
metadata is written as a reStructuredText docinfo field list rather than YAML
front matter, because the rest of this repository's documentation is
reStructuredText and docinfo is its native mechanism for exactly this.


Metadata fields
===============

``Status``
    ``Open`` -- filed, no decision yet.
    ``Accepted`` -- agreed it should be fixed, not started.
    ``In progress`` -- being worked on.
    ``Fixed`` -- done; put the commit in ``Resolution``.
    ``Rejected`` -- decided against; put the reasoning in ``Resolution``.
    ``Deferred`` -- real, but not now.

``Claimed`` (optional)
    Names the branch, worktree or task that has this issue in hand right now,
    so nobody starts it twice. Written just after ``Status``, and **deleted by
    the change that resolves the issue**, in the same commit that sets
    ``Status: Fixed``. It is the only optional field; every other one is always
    present.

    ``Status: In progress`` is not a substitute, which is why this exists.
    A branch is claimed the moment it is cut, while the issue is still
    ``Accepted`` and the maintainer has not yet agreed it is being worked --
    044 was in exactly that state -- and a status set on a branch is invisible
    on ``master``, where the next person looks. ``In progress`` also cannot say
    *where* the work is, which is the one thing that stops the duplicate.

``Severity``
    ``High`` / ``Medium`` / ``Low``. Judged by user-visible impact, not by how
    hard it is to fix.

``Area``
    Roughly which part of the system, so related issues can be read together.

``Reported`` / ``Source``
    When it was found and what found it.

``Evidence``
    The test that pins the current behaviour, where one exists. Every issue
    below that describes a defect has one: the suite asserts what the code does
    *today*, so fixing the issue means deliberately changing a test rather than
    discovering a surprise.

``Depends on`` / ``Blocks`` / ``Related``
    How this issue sits against the others. ``Depends on`` lists the issues that
    should be settled or fixed **before** this one, with the reason; ``Blocks``
    is the same relation seen from the other end; ``Related`` is shared code, a
    shared decision or a shared cause with no ordering implied. ``Depends on``
    and ``Blocks`` are kept consistent in both directions, so the graph can be
    read from either file. ``(none)`` means exactly that -- the field is always
    present, so a missing edge is a statement rather than an omission.

    The order these dependencies imply is worked out once, for the whole list,
    in :doc:`index` under "Suggested order of implementation".

``Decision``
    Left as ``undecided`` until the maintainer rules on it. This is the field to
    fill in when reviewing the list.

    An agent that needs a ruling asks for one, but does not wait for it. If the
    work reaches the point where only the ruling is missing, decide on the
    evidence and write both halves here -- what was asked, what came back or
    that nothing did, and what was therefore chosen. 031 is the shape: it
    records that the maintainer was asked, what was chosen, and that the
    evidence would have carried the same ruling alone.

``Resolution``
    Commit, or the reason for rejecting. Write the commit as soon as you have
    it, on the branch that makes it. The rebase onto ``master`` then rewrites
    that commit and leaves this field naming one that is on no branch, so run
    ``dev/repoint --write`` after the rebase: it finds each dead pointer and
    names the commit that landed. "A commit named before it lands" below says
    when, and what runs it. The build fails on a pointer nobody re-pointed.


Stages, in the plans
====================

An issue is one problem. A *stage* is one step of a programme that was planned
as a whole: :doc:`../upgrade-plan`'s twenty, and :doc:`../test-coverage-plan`'s
packages. They are not issues -- there is nothing to decide about them and
nothing to rank, because the plan already argued for the order -- but "what is
next" has to be answerable without reading a hundred kilobytes of reasoning.

So each stage heading carries a field list of its own::

    Stage 4 — Photologue 2.8.3 → 3.0.2, still on Django 1.6
    --------------------------------------------------------

    :Status: Next

``Status`` is ``Done``, ``Next`` or ``Planned``, and the three read as a ladder:
everything above ``Next`` is done, everything below it is not, and exactly one
stage is ``Next`` until the plan is finished, at which point none is and the
plan stops asking to be read. ``Done`` also carries ``Resolution`` -- the commit
that landed it, or the issues that did -- and those commits are checked like an
issue's. ``Stage`` names the step where the heading does not, as
``test-coverage-plan``'s infrastructure section does.

The prose around a stage is unchanged: it is the argument for doing it that
way and the record of what it cost. The field is the one line a machine reads,
and "Where this plan has got to" at the top of each plan is generated from it.


Removed documents, and the archive
==================================

Text this project no longer wants is removed with ``git rm`` rather than left
in place with a note saying it is out of date. Git keeps the content; the
pointer to it goes in ``docs/archive.rst``, one bullet per removed document::

    * ``docs/issues/incoming.rst`` @ ``88455a0`` -- the "Emptied on ..."
      entries, removed 2026-08-04. Why they went, in as many lines as it takes.

The path and the commit are literals, separated by ``@``, and the reason
follows ``--`` and wraps onto indented lines. **Name a commit that is already
on** ``master``, and not one the removing branch makes itself. Any older commit
that still holds the file will do, and the head of ``master`` at the time of
writing is the obvious one, so this pointer never needs re-pointing at all.

The build reads that page and asks ``git`` whether each pointer resolves, and
whether that commit really does hold the file, so an archive entry is a promise
the documentation keeps rather than one it makes.


A commit named before it lands
==============================

Write the hash when you have it. Re-point it when the branch lands:

1. ``git rebase master``.
2. ``dev/repoint`` -- what each dead pointer became, and how it was worked out.
3. ``dev/repoint --write`` -- the same, written into the files.
4. Commit that, then merge the branch with ``--no-ff``. A merge does not
   rewrite a commit, so what you wrote in step 3 is still true afterwards.

This replaces the rule that said to write nothing until the branch had landed.
That rule was correct and nobody kept it: eighteen dead pointers reached
``master`` under it, because "write the fix and the issue file in one commit"
and "write the hash after that commit lands" cannot both be obeyed at once.
A step that runs beats a rule that asks somebody to come back later.

**Who runs it.** Whoever lands the branch, as step 3 of landing it. The
documentation build is what notices when nobody did: it fails, names every dead
pointer at once, and names this command. Continuous integration can only
notice, never repair -- it clones the repository fresh, so it holds neither the
old commit nor the record of what became of it.

**How it knows.** Three sources, best first. ``dev/post-rewrite`` is a hook
``git`` calls after every rebase and amend, with the ``old new`` pairs it just
made; install it once per clone, as its own comment says. Failing that, the
patch identity: the same judgement ``git rebase`` itself makes about whether a
commit is already upstream. Failing that, the commit subject, which survives a
conflict that changed the patch. A pointer none of the three can map is
reported for a person to settle, never guessed at.

**What it cannot do.** A commit ``git gc`` has pruned is gone, and no hash in
any document will bring it back. The hook is what makes the mapping survive
that, because it writes the pair down while both commits still exist.

**A hash with no letter in it is invisible to the check.** The register reads a
commit as a hex run with both a digit and a letter, which is what keeps
``max-age=31536000`` out of it. About one abbreviation in fifty is all digits,
and 059 was re-pointed at ``7200893`` before anybody noticed. ``dev/repoint``
now writes such a hash long enough to reach a letter; a hash typed by hand
wants the same care.

**A commit that is deliberately not on** ``master`` **needs a tag.** Issue 062
names a spike that was measured and abandoned. A tag holds it, so ``git`` can
still reach it, and the build reads it as parked rather than as rot. Without
the tag the two are indistinguishable.


What the build checks
=====================

These fields are read by machine as well as by people: :doc:`next` -- the queue
of what is ready to work on -- is generated from them every time the
documentation is built, and so is each ranking table in :doc:`index`. Nothing
about a status is written down twice, so nothing about a status can drift.

``dev/kasvimuseo docs`` fails, rather than rendering something stale, when

* a field above is missing, empty, given twice, or spelled in a way this page
  does not define,
* ``Status`` or ``Severity`` carries a value that is not in the lists above,
* an issue file is missing from :doc:`index`'s suggested order, or appears in
  it twice -- the promise that "every issue appears exactly once" is enforced
  rather than hoped for,
* that order names an issue with no file,
* a ``Depends on`` or ``Blocks`` field names an issue that has no file, or one
  that does not name it back. Both halves matter: an edge pointing at nothing
  used to be *dropped* from the queue, so a mistyped number read as "ready
  now", and an edge recorded at one end only cannot be read from the other,
* a plan's stages do not read as a ladder: two are ``Next``, a ``Done`` one sits
  below an unfinished one, work is left and nothing says which piece is next, or
  a ``Done`` stage does not say what landed it,
* a commit named in a ``Resolution`` field, whether an issue's or a stage's, or
  in an archive entry, is one that nothing reaches: no branch, no tag, and in
  the worst case no object either. That is what a pointer written before a
  rebase becomes, and the message names every one of them and the command that
  repairs them. A commit that is only on the branch you are working on passes,
  because a branch reaches it; it is the next rebase that kills it, and
  ``dev/repoint`` that saves it. A checkout that cannot answer -- a shallow
  clone, one without ``git``, one with no ``master`` -- reports that it skipped
  the check and does not fail.

  Reachability is the question, not existence. The checkout that wrote a dead
  pointer keeps the old commit as a dangling object for as long as ``git gc``
  leaves it, so the pointer resolves there and nowhere else. Eighteen of them
  had accumulated on ``master`` under a check that asked whether the object was
  present.

Writing about a generated page: name the fields, not the table
--------------------------------------------------------------

A generated table exists only after a build. Half this project's readers are
looking at the repository rather than the published site, and what they find
where the table should be is ``.. issue-queue::`` and nothing else -- so an
instruction to "take the top row" or "count the rows" is an instruction they
cannot follow, and one they can misread as "there is no work".

So point at what the table is made of. "The issues whose ``Status`` is ``Open``
or ``Accepted`` with no ``Claimed``" is true in both places, and it says how the
built table differs: it also drops the ones waiting on a dependency. Both of
this convention's authors wrote the other kind first, in the same week, which
is why it is written down here.

The parser is ``docs/_ext/issue_register.py`` and the directives are in
``docs/_ext/sphinx_issue_register.py``; both are covered by
``kasvimuseo/tests/test_issue_register.py``.

Issue history
=============

Each issue owns its history. Read :doc:`index` for the complete register.
The private deployment repository owns installation-specific reports and the original register commentary.
