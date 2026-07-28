======
Issues
======

One file per known problem, numbered in the order it was filed, each with a
``Status`` field that is the thing actually tracked. The register below explains
the convention and groups the issues by where they came from; every issue is
also listed individually, and a new file appears here without editing anything.

.. toctree::
   :maxdepth: 1

   The register and its conventions <README>
   Reported, not yet split into files <incoming>

Suggested order of implementation
=================================

The file numbers record when an issue was filed, not what to do first. This is
the order to do them in. Every issue appears exactly once.

Each issue carries ``Depends on``, ``Blocks`` and ``Related`` fields naming the
others it touches; the groups below are the order those constraints allow,
resolved once here rather than rediscovered per issue. No group is a barrier --
anything can be pulled forward as long as its ``Depends on`` list is already
done.

How this is ranked
------------------

* **A clear bug with an obvious fix outranks everything else.** If the code is
  plainly not doing what it was written to do, and the repair does not need a
  product decision, it goes first regardless of severity label.
* **A bug whose fix needs a ruling is ranked by whether a safe interim exists.**
  Issue 041 crashes today and has an option that stops the crash without
  settling the underlying question, so it is early. Issue 001 changes what the
  public site lists either way, so it waits for the maintainer.
* **Cheap deletions are cheap, but they buy nothing on their own.** They sit
  behind everything user-visible, and ahead of the upgrade, which is the work
  they exist to make smaller.
* **The upgrade is last** because it is a programme rather than a fix, and
  because most of the list is a prerequisite for it.

1. Find out what is actually true
----------------------------------

Before anything else, and independent of all of it. None of these is a code
change yet; each changes what the rest of the list means. The first two are a
question to whoever reported them, the last two a look at the server.

==== ======== =============================================================
  ID Severity Why first
==== ======== =============================================================
 044 High     If the save buttons really are gone, the species data cannot
              be edited at all, which outranks everything below. It could
              not be reproduced -- they render, and they are visible and
              clickable in a browser -- so the next step is four questions
              to the reporter, not a commit.
 045 Medium   "Everything works on an iPad" has no scope yet. The answer
              decides whether this is one ``<meta>`` tag or a rewrite of
              the label editor's drag-and-drop, and it may also answer 044.
              Once scoped, its parts rank themselves among the groups
              below.
 026 Medium   The answer is either "the deployment is not reproducible" or
              "production is serving with ``DEBUG`` on", which is a live
              information-disclosure problem. One look at the server
              settles which, and nothing else on this page can.
 025 High     Rotating the ``SECRET_KEY`` and the database password costs
              one round of logouts. It depends on nothing and it is in the
              file the upgrade will edit repeatedly.
==== ======== =============================================================

2. Crashes on real data
-----------------------

Each is a 500 reachable today, each has a fix that needs no product decision.

==== ======== =============================================================
  ID Severity Why here
==== ======== =============================================================
 002 High     A ``post_save`` receiver registered for every model can raise
              on any save. The largest blast radius on the list, and 042
              cannot be done until it is fixed.
 009 Medium   The ``Create Species Sheets`` action 500s on a species with
              no ``external_id``, which the production data has.
 041 Medium   Eight of 311 observation pages 500 on a link that this
              repository has just made reachable. Option 1 stops the crash
              without waiting for the ruling on what a duplicate number
              means.
 008 Medium   A 500 on a fresh database, so it is the first thing a new
              developer meets and the first thing CI would hit (018).
==== ======== =============================================================

3. Visibly broken pages
-----------------------

Small, self-contained, each visible to a visitor or to the gardeners.

==== ======== =============================================================
  ID Severity Why here
==== ======== =============================================================
 004 Medium   A broken image on every observation page; deleting one tag
              fixes it.
 005 Medium   The species-list search box is switched off by an ``X``
              prefix on four attributes. The feature was built and then
              disabled; turning it back on is a four-character edit.
 007 Low      An unknown species id renders a blank page instead of 404.
              Same family as 041, and cheapest done alongside it.
 040 Medium   Half the admin chrome is English on a Finnish-only
              application, on the page it opens on. One line per image
              definition -- but it changes how the application is built,
              which is why it is here rather than in group 2.
 043 Low      The one column the photo changelist is searched by is the one
              that cannot be sorted. One attribute, cause known, and the
              only reported issue whose fix needs no decision at all.
 047 Medium   The label editor's print toggle is drawn with a character no
              Linux font carries, and its ``<label for>`` points at nothing,
              so the symbol is both invisible and inert. Pick a printer and
              fix the ``for`` in the same edit.
 046 Low      The same page opens at printed size, so arranging labels
              starts with a manual zoom. Last of this group: a safe interim
              exists -- the browser's own zoom -- and the fix wants a ruling
              on whether the page gets a control or just a smaller default.
==== ======== =============================================================

4. The photo path
-----------------

One cluster, and it should be done as one: four of these five are the same
receiver or the same handler, and the documentation at the end describes
whatever they settle on. Doing 037 first would document behaviour that is about
to change.

==== ======== =============================================================
  ID Severity Why here
==== ======== =============================================================
 003 Medium   Photo-to-species matching is case-sensitive on one side and
              not the other, so photos silently fail to attach. One
              shared helper fixes both call sites.
 042 Medium   A species photo cannot be replaced once set -- the capability
              behind most of the confusion. Needs 002 first, because
              dropping ``photo__isnull=True`` widens exactly that fault.
 039 Medium   The per-label photo choice has been written and never read
              back since 2018. Decide it before 037, because option 3
              there says the opposite thing depending on the answer.
 010 Medium   The same ``post`` handler as 039, pairing items to labels by
              position. Cheapest fixed while that code is already open.
 011 Medium   The species report opens every image file on every render to
              choose a CSS class -- the cause of the ``IOError`` the README
              warns about, and the reason ``media fetch`` exists.
 037 Medium   The in-UI instructions. Last in the group by construction:
              it depends on 002, 003, 039 and 042, and its whole content
              is what those four decide.
==== ======== =============================================================

5. public_planted
-----------------

Ordered deliberately: fix the cost first, then change the meaning, so the
semantic change lands on code that is already correct about queries.

==== ======== =============================================================
  ID Severity Why here
==== ======== =============================================================
 012 Medium   One ``COUNT`` per planting, from a ``prefetch_related`` that
              is defeated by ``.count()``. Behaviour-preserving, so it is
              the safe half of the work.
 001 High     ``SpeciesManager`` ignores ``removal_date`` while the other
              two managers do not, so removed species stay on the public
              list. High severity, but it is a decision about what the
              public site means, not a repair -- hence behind 012 and
              behind the unambiguous bugs.
==== ======== =============================================================

6. Defensive settings and Python 3 landmines
--------------------------------------------

All four are no-ops today. That is the point: each converts a future silent
failure into a visible line of code, and each is cheapest now, while nothing
depends on it.

==== ======== =============================================================
  ID Severity Why here
==== ======== =============================================================
 019 High     Write ``MIDDLEWARE_CLASSES`` out explicitly. Today a no-op;
              at Django 2.0 its absence silently removes sessions, auth
              and CSRF. Also the prerequisite for 023.
 023 Medium   Add ``django.contrib.messages`` to ``INSTALLED_APPS``, and
              its middleware to the list 019 just created.
 024 Medium   Delete the ``python2.7`` site-packages path from
              ``TEMPLATE_DIRS``. It is unnecessary today and a silent
              blocker at the Python 3 flip.
 016 Medium   ``remove_diacritics`` returns an iterator on Python 3, which
              would corrupt every derived photo slug with no error. The
              replacement behaves identically on both versions.
==== ======== =============================================================

7. Deletions and tidying
------------------------

Nothing here changes behaviour. Together they remove two dead apps, a dead
route, a dead deployment, a dead template and a set of comments that describe
the code wrongly -- and they shrink what the upgrade has to carry. Ordered so
that 032 comes before 031, which it partly resolves.

==== ======== =============================================================
  ID Severity Why here
==== ======== =============================================================
 020 Low      Two abandoned apps in ``INSTALLED_APPS`` that must otherwise
              keep importing under 19 future Django versions.
 021 Low      ``gunicorn`` as an installed app, for a management command
              that no longer exists.
 022 Low      A ``/media/grappelli/`` route pointing at a directory that
              does not exist, plus a setting Django removed in 1.4. Also
              one of the three string-view routes Django 1.10 rejects.
 033 Low      ``django-pserver`` installed everywhere and never enabled.
 032 Low      ``fabfile.py`` is a second, stale deployment next to the
              maintained Ansible one. Deleting it removes ``flax``.
 031 Medium   The remaining URL dependencies. ``django-jqm`` is the one
              that matters: vendoring it takes a personal GitHub URL out
              of the production build path.
 006 Low      165 lines of template nothing references, which would render
              wrongly if it were ever wired up.
 013 Low      Two standing ``FIXME`` comments that the tests disprove, so
              readers avoid features that work.
 015 Low      Mixed integer and float division in generated CSS. Valid
              output either way; last because it is the only item on this
              page with no consequence at all.
==== ======== =============================================================

8. Make the work verifiable
---------------------------

These do not fix anything. They decide how often everything above is checked,
which is what makes the rest of this page hold.

==== ============ =========================================================
  ID Severity     Why here
==== ============ =========================================================
 018 Medium       No CI. The suite needs PostgreSQL, no dump, no media, and
                  runs in ten seconds -- it is unusually ready for a
                  pipeline. Ahead of 017 because it is the cheaper half and
                  017 needs somewhere to run.
 017 High         The 626-line Vue label editor has no behavioural test,
                  and the suite meant to cover it cannot start. Either
                  rebuild it on ``LiveServerTestCase`` or delete it so it
                  stops looking like coverage.
 038 Low          Already in progress; listed for completeness. Its
                  remaining work is triggered by 018 and by Stage 10.
==== ============ =========================================================

9. The upgrade programme
------------------------

Last, and in this internal order. The decisions come before the mechanical
work, because both 034 and 027 are cheap to decide now and expensive to decide
late.

==== ======== =============================================================
  ID Severity Why here
==== ======== =============================================================
 034 High     Decide the fate of the ``admin_list`` fork **before Stage
              6**. Carried stage by stage it is plausibly the largest
              single cost in the whole upgrade, and it fails silently.
 014 Low      Dead code inside that same file. Moot if 034 retires it,
              which is why it waits.
 028 Medium   Pillow ceiling.
 029 Low      setuptools ceiling on gunicorn.
 030 Low      Build-tool floor for early ``django-sortedm2m``.
 027 High     The lock. It has to record 028, 029 and 030, so it comes
              after them; it also makes ``--no-deps`` unnecessary and
              ``setup.py`` honest, which is a benefit today.
 036 High     The programme itself: 20 stages, planned in
              :doc:`../upgrade-plan`. Everything above is either a
              prerequisite of it or work that gets harder once it starts.
 035 Low      Nothing to do now. Revisit once the upgrade lands, while the
              cost of being paced by two third-party packages is fresh.
==== ======== =============================================================

All issues
==========

.. toctree::
   :maxdepth: 1
   :glob:

   [0-9]*
