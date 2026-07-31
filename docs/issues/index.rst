======
Issues
======

One file per known problem, numbered in the order it was filed, each with a
``Status`` field that is the thing actually tracked. The register below explains
the convention and groups the issues by where they came from; every issue is
also listed individually, and a new file appears here without editing anything.

**To pick up work, read** :doc:`next` **instead of this page.** It is the
ranking below with every issue's current ``Status`` folded in, generated from
the issue files at build time, plus the handful of facts a fresh session needs
before it can start.

.. toctree::
   :maxdepth: 1

   What to work on next <next>
   The register and its conventions <README>
   Reported, not yet split into files <incoming>

Suggested order of implementation
=================================

The file numbers record when an issue was filed, not what to do first. This is
the order to do them in. Every issue appears exactly once -- the build fails
otherwise, because :doc:`next` is generated from this order.

The tables below are the order itself: each is an ``issue-rank`` directive
whose body is ``NNN: why it is here``, which is both what renders and what
:doc:`next` reads. The severity beside it comes from the issue file, so it
cannot drift. The ranking is the one judgement here that no script can
reproduce, which is why it is written out next to the argument for it.

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
  Issue 041 crashed on live data and had an option that stops the crash without
  settling the underlying question, so it was early, and that option is what it
  got. Issue 001 changes what the
  public site lists either way, so it waits for the maintainer.
* **Cheap deletions are cheap, but they buy nothing on their own.** They sit
  behind everything user-visible, and ahead of the upgrade, which is the work
  they exist to make smaller.
* **The upgrade is last** because it is a programme rather than a fix, and
  because most of the list is a prerequisite for it.

1. Find out what production actually runs
-----------------------------------------

Before anything else, and independent of all of it. None is a code change; each
changes what the rest of the list means.

.. issue-rank::

   050: A working superuser password for the production admin has been in a
      tracked file since 2020, and is still the password that account uses.
      First of these three because it needs no access to anything to use and
      one command to end, and because the file it was in has just been deleted
      -- which changes nothing until the password does.
   049: The rotated ``SECRET_KEY`` and database password are in the vault and
      not in use, so the disclosure 025 describes is still live. One playbook
      run ends it, and it is the only item on this page whose timing belongs to
      somebody outside the project.
   026: The answer is either "the deployment is not reproducible" or
      "production is serving with ``DEBUG`` on", which is a live
      information-disclosure problem. One look at the server settles which,
      and nothing else on this page can.
   025: Rotating the ``SECRET_KEY`` and the database password costs one round
      of logouts. It depends on nothing and it is in the file the upgrade will
      edit repeatedly.

2. Broken on real data
-----------------------

Each is reachable today, each has a fix that needs no product decision -- with
one exception, 048, last in the group: it came from the same machine pair as
044 and what it needed was a ruling on a deliberate design rather than a
repair. It has that ruling, and the fix.

.. issue-rank::

   044: Six of the admin's change forms are cut off mid-response for a browser
      on another machine, taking the submit row with them, so those models
      cannot be edited at all. Everything over roughly 43 KB is affected. The
      application renders them correctly; the loss is in ``runserver``, the
      container's port publication or the tailnet. First because it is what
      stops the maintainer working today, and because a truncated form must
      not be saved.
   002: A ``post_save`` receiver registered for every model can raise on any
      save. The largest blast radius on the list, and 042 cannot be done until
      it is fixed.
   009: The ``Create Species Sheets`` action 500s on a species with no
      ``external_id``, which the production data has. **Fixed**: those species are
      skipped and named in an admin message.
   041: Eight of 311 observation pages 500'd on a link that this repository had
      just made reachable. **Fixed as far as the crash goes**: option 1, the
      first match by primary key. The ruling on what a duplicate number means
      is still owed.
   008: A dead gallery index on a fresh database, so it was the first thing a
      new developer met and the first thing CI would have hit (018).
      **Fixed**: the route is overridden with ``allow_empty=True``, and it
      answered 404 rather than the 500 reported here.
   048: The development server named the production media host in every photo
      URL and served no media of its own, so a photo added or replaced in
      development 404'd and the fetched local copies were never the ones shown.
      **Fixed**: option 3, local files first with the production host as the
      fallback, so nothing has to be downloaded before a photo appears.

3. Visibly broken pages
-----------------------

Small, self-contained, each visible to a visitor or to the gardeners.

.. issue-rank::

   004: A broken image on every observation page; deleting one tag fixes it.
      **Fixed**: option 1, the tag is gone. It was scaffolding left in the
      commit that added the page, not a photo that went missing.
   005: The species-list search box is switched off by an ``X`` prefix on three
      attributes. **Fixed**: option 1, the prefixes are gone. The history shows
      the feature was never disabled -- the ``X`` was a work-in-progress marker
      in the commit that wrote the page, applied to the loop variable as well.
   007: An unknown species id rendered a blank page instead of 404. **Fixed**:
      same family as 041, and it was done alongside it.
   040: Half the admin chrome is English on a Finnish-only application, on the
      page it opens on. One step per image definition -- but it changes how
      the application is built, which is why it is here rather than in group
      2. **Fixed**: Django's stray ``data_files`` tree is moved back into the
      package, and only the development image was ever affected.
   043: The one column the photo changelist is searched by is the one that
      cannot be sorted. One attribute, cause known, and the only one of the
      five reports that never needed a ruling: it arrived as work rather than
      as a question.
   046: The label editor opens at printed size, so on the iPad it shows one
      label per row and will not zoom out. Ruled: 50 % on screen, print
      unaffected. One rule in ``@media screen``, plus the drag preview's
      matching constant.
   047: The same page's print toggle is drawn with a character no Linux font
      carries, and its ``<label for>`` points at nothing, so the symbol is
      both invisible and inert. Ruled: an inline SVG, with the checkbox
      wrapped in the label so clicking the icon toggles it. Take it before 045
      drops the hover, which is what currently keeps it off the paper.
   045: The rest of the tablet work, now that its scope is settled: a viewport
      tag, a print button, and a toggle that does not need a hover. Its large
      half -- replacing drag-and-drop with pointer events so numbers can be
      moved by touch -- is deliberately not here; it wants the browser suite
      of 017 first, since it rewrites the one part of the editor no test can
      see.

4. The photo path
-----------------

One cluster, and it should be done as one: four of these five are the same
receiver or the same handler, and the documentation at the end describes
whatever they settle on. Doing 037 first would document behaviour that is about
to change.

.. issue-rank::

   003: Photo-to-species matching is case-sensitive on one side and not the
      other, so photos silently fail to attach. One shared helper fixes both
      call sites.
   042: A species photo cannot be replaced once set -- the capability behind
      most of the confusion. Needs 002 first, because dropping
      ``photo__isnull=True`` widens exactly that fault.
   039: The per-label photo choice has been written and never read back since
      2018. Decide it before 037, because option 3 there says the opposite
      thing depending on the answer.
   010: The same ``post`` handler as 039, pairing items to labels by position.
      Cheapest fixed while that code is already open.
   011: The species report opens every image file on every render to choose a
      CSS class -- the cause of the ``IOError`` the README warns about, and
      the reason ``media fetch`` exists.
   037: The in-UI instructions. Last in the group by construction: it depends
      on 002, 003, 039 and 042, and its whole content is what those four
      decide.

5. public_planted
-----------------

Ordered deliberately: fix the cost first, then change the meaning, so the
semantic change lands on code that is already correct about queries.

.. issue-rank::

   012: One ``COUNT`` per planting, from a ``prefetch_related`` that is
      defeated by ``.count()``. Behaviour-preserving, so it is the safe half
      of the work. **Fixed**, though not as reported: the prefetched
      ``.count()`` costs nothing, and the per-planting query was
      ``is_public_planted`` reading an unfetched ``bed``.
      ``ObservationManager`` now prefetches it.
   001: ``SpeciesManager`` ignores ``removal_date`` while the other two
      managers do not, so removed species stay on the public list. High
      severity, but it is a decision about what the public site means, not a
      repair -- hence behind 012 and behind the unambiguous bugs.

6. Defensive settings and Python 3 landmines
--------------------------------------------

All four are no-ops today. That is the point: each converts a future silent
failure into a visible line of code, and each is cheapest now, while nothing
depends on it.

.. issue-rank::

   019: Write ``MIDDLEWARE_CLASSES`` out explicitly. Today a no-op; at Django
      2.0 its absence silently removes sessions, auth and CSRF. Also the
      prerequisite for 023.
   023: Add ``django.contrib.messages`` to ``INSTALLED_APPS``. Its middleware
      is already in the list 019 wrote out, being part of the 1.5 default.
   024: Delete the ``python2.7`` site-packages path from ``TEMPLATE_DIRS``. It
      is unnecessary today and a silent blocker at the Python 3 flip.
   016: ``remove_diacritics`` returns an iterator on Python 3, which would
      corrupt every derived photo slug with no error. The replacement behaves
      identically on both versions.

7. Deletions and tidying
------------------------

Nothing here changes behaviour. Together they remove two dead apps, a dead
route, a dead deployment, a dead template and a set of comments that describe
the code wrongly -- and they shrink what the upgrade has to carry. Ordered so
that 032 comes before 031, which it partly resolves.

.. issue-rank::

   020: Two abandoned apps in ``INSTALLED_APPS`` that must otherwise keep
      importing under 19 future Django versions.
   021: ``gunicorn`` as an installed app, for a management command that no
      longer exists.
   022: A ``/media/grappelli/`` route pointing at a directory that does not
      exist, plus a setting Django removed in 1.4. Also one of the three
      string-view routes Django 1.10 rejects.
   033: ``django-pserver`` installed everywhere and never enabled.
   032: ``fabfile.py`` is a second, stale deployment next to the maintained
      Ansible one. Deleting it removes ``flax``.
   031: The remaining URL dependencies. ``django-jqm`` is the one that
      matters: vendoring it takes a personal GitHub URL out of the production
      build path.
   006: 165 lines of template nothing references, which would render wrongly
      if it were ever wired up.
   013: Two standing ``FIXME`` comments that the tests disprove, so readers
      avoid features that work.
   015: Mixed integer and float division in generated CSS. Valid output either
      way; last because it is the only item on this page with no consequence
      at all.

8. Make the work verifiable
---------------------------

These do not fix anything. They decide how often everything above is checked,
which is what makes the rest of this page hold.

.. issue-rank::

   018: No CI. The suite needs PostgreSQL, no dump, no media, and runs in ten
      seconds -- it is unusually ready for a pipeline. Ahead of 017 because it
      is the cheaper half and 017 needs somewhere to run.
   017: The 626-line Vue label editor has no behavioural test, and the suite
      meant to cover it cannot start. Either rebuild it on
      ``LiveServerTestCase`` or delete it so it stops looking like coverage.
      **Fixed**, and by neither: there is no maintained browser stack for
      Python 2.7, so the tests are Python 3 on the host driving Playwright
      against the real application, and the old suite is deleted. The password
      it carried turned out to be live, which is 050.
   038: Already in progress; listed for completeness. Its remaining work is
      triggered by 018 and by Stage 10.

9. The upgrade programme
------------------------

Last, and in this internal order. The decisions come before the mechanical
work, because both 034 and 027 are cheap to decide now and expensive to decide
late.

.. issue-rank::

   034: Decide the fate of the ``admin_list`` fork **before Stage 6**. Carried
      stage by stage it is plausibly the largest single cost in the whole
      upgrade, and it fails silently. Decided: retired, with the deletion
      scheduled for Stage 5, where Django's own ``field-`` classes arrive.
   014: Dead code inside that same file. It waited for 034 and 034 answered it:
      the file has a deletion date, so there is nothing here to repair. Left
      open only because the file is still in the tree; it closes with it.
   028: Pillow ceiling.
   029: setuptools ceiling on gunicorn.
   030: Build-tool floor for early ``django-sortedm2m``.
   027: The lock. It has to record 028, 029 and 030, so it comes after them;
      it also makes ``--no-deps`` unnecessary and ``setup.py`` honest, which
      is a benefit today.
   036: The programme itself: 20 stages, planned in :doc:`../upgrade-plan`.
      Everything above is either a prerequisite of it or work that gets harder
      once it starts.
   035: Nothing to do now. Revisit once the upgrade lands, while the cost of
      being paced by two third-party packages is fresh.

All issues
==========

.. toctree::
   :maxdepth: 1
   :glob:

   [0-9]*
