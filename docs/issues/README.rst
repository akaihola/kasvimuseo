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

``Resolution``
    Commit, or the reason for rejecting.


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
* that order names an issue with no file.

The parser is ``docs/_ext/issue_register.py`` and the directives are in
``docs/_ext/sphinx_issue_register.py``; both are covered by
``kasvimuseo/tests/test_issue_register.py``.


Open issues
===========

All but 001, 002, 003, 004, 005, 006, 007, 008, 009, 010, 011, 012, 013, 014,
015, 016, 017,
019, 020, 021, 022, 023, 024, 025, 026, 027, 031, 033, 034, 037, 038, 039, 040,
041, 042, 043, 046, 047, 048, 053 and 054 are open: each one
either changes
behaviour that is visible in production, deletes code, or commits to a piece of
work, so each wants a decision first. Nine of the
exceptions -- restoring an action that crashes, two missing lookup guards, an
archive view that refused to render an empty list, a missing sort link the
maintainer asked to have done rather than ruled on, a placeholder image, a
search box switched off by a typo, a receiver that could raise on any save, and
a ``filter()`` that returns an iterator on Python 3 where the replacement is
correct on both -- needed no ruling, and stay in the tables with
``Status: Fixed``. 040 and 048
did need one -- 040 between its three options, 048 between three shapes of a
deliberate design change -- and both were ruled and fixed the same day; their
files carry the reasoning. 037 needed one between four options and got it once
the four issues its content depends on were all fixed: three were taken and the
fourth, a separate page repeating them, was not. 011's three options settled
themselves once the pinned photologue was read rather than argued about: the
cheap one was not there, so the expensive one was the only one, and the file
records what was looked at as well as what was chosen.
031 needed one as well, between vendoring the fork and publishing it to a
package index -- the second is not this repository's to do, but it was a real
option and the field said ``undecided``, so it was asked rather than assumed;
the maintainer chose vendoring, and the file records that the evidence would
have carried the same ruling alone.
042 needed one too, and got it when the defect it
describes was reported from the garden a second time, as a species photo that
would not change; it is the reason 002 had to be fixed first, and the two are
``Fixed`` together. 003 needed one as well -- where the normalisation its two
matching sites have to share lives, and whether Python or PostgreSQL folds the
case -- and its file carries both, including why the second answer takes a
different shape from 043's on the same data. 041 is fixed only as far as its
crash goes: the product
question inside it is still open, which is why its ``Status`` says so. 004 and
005 arrived with options that looked like questions and were not: in both, ``git
log`` showed the defect was left-behind scaffolding rather than a decision
anybody had made, so the ``Decision`` on each records what the history settled
rather than a ruling the maintainer still owed. 025 is the one whose work splits
between two owners, and the split is why it is ``Fixed`` while the problem it
describes is not solved: the repository stopped carrying the production
``SECRET_KEY`` and database password and now reads them from the environment,
which is everything this repository can do and which remediates nothing by
itself. Deploying the rotated values -- the act that ends the disclosure -- is
049, and it is open. 025's file says so at the top rather than reading as a
completed remediation. 001 needed one between two readings of the same page -- what the garden holds
now, or what it has held -- and the maintainer took the first, so the public
species list lost the species whose plantings have all been removed. Its file
records the argument as well as the ruling, including the two places that had
already assumed the answer: the method's own docstring and the species detail
page's bed list. 012 needed no ruling either, being purely about query
cost, but it is the one whose report was wrong: the ``COUNT`` in its title is
free under ``prefetch_related``, and the query that actually scaled per planting
was the bed behind ``is_public_planted``. Its file keeps the original diagnosis
and adds the measurement that overturns it, since the reasoning is the useful
part.

This page groups them by **where they came from**, which is how to read them.
For the order to *do* them in, which cuts across those groups, see "Suggested
order of implementation" in :doc:`index` -- or :doc:`next`, which is that order
with the statuses folded in and everything unactionable taken out.

They come from seven pieces of work. **001-018** came out of the test coverage
work on branch ``test-coverage_g78``; each has a test pinning the current
behaviour, so fixing one means deliberately changing a test.
**019-036** came out of the dependency and platform upgrade analysis on branch
``requirements-update-plan`` (``docs/upgrade-plan.rst``). Those mostly have no
``Evidence`` entry, because they concern configuration, packaging and future
versions rather than code paths a test can reach.
**037 and 039** came out of a later walkthrough of how photo management is meant
to be used: 037 is about missing documentation rather than a defect, and 039 is a
defect the suite happens not to reach, so neither has an ``Evidence`` entry.
**038** came out of setting up this documentation build on branch ``sphinx-docs``.
**040 and 041** came out of walking through the admin front page on branch
``dashboard-usability``: 040 is a packaging accident in a dependency rather than
anything this repository does wrong, so it had no ``Evidence`` entry until it
was fixed and two assertions about Django's own strings were added with the fix,
while 041 is a defect the suite reaches only with unique test data.
**042** was written as an implementation plan on branch
``species-photo-always-switch`` and filed here instead, since the change it
proposes wants a decision before it is made.
**043-047** were reported by the maintainer rather than found by a piece of
work, and were split out of ``incoming.rst``. They are the only ones written
from somebody using the application, so they arrived as symptoms; the detail
that placed them -- browser, device, which models, and finally a copy of the
delivered page -- came from asking. 044's cause was only visible in that last
one, and it is not in the application.

From the test coverage work
---------------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 001 High     models / public site    Public species list shows removed species
 002 High     models / admin          Photo auto-attach can break every Photo save
 003 Medium   models / photos         Photo-to-species matching is case-sensitive
 004 Medium   templates / public      Broken placeholder image on every observation page
 005 Medium   templates / public      Search box on the public species list is disabled
 006 Low      templates / cleanup     Dead template: planted-species-compact.html
 007 Low      views / public site     Unknown species id renders empty page, not 404
 008 Medium   urls / third party      Photologue gallery index raises on empty database
 009 Medium   admin                   Create Species Sheets breaks without external id
 010 Medium   views / labels API      Labels API pairs items to labels by position
 011 Medium   templates / operations  Species report opens every image to pick a class
 012 Medium   models / performance    public_planted issues one COUNT per planting
 013 Low      admin / documentation   Stale FIXME comments claim features are broken
 014 Low      templatetags / vendored Dead code in the vendored identifier_for_field
 015 Low      templatetags / frontend bush_shadow mixes integer and float division
 016 Medium   forms / py3 migration   remove_diacritics silently breaks on Python 3
 017 High     tests / gap             Browser suite unrunnable, Vue editor untested
 018 Medium   process                 No CI: the suite is only ever run by hand
==== ======== ======================= ==================================================

Suggested reading order for a first review: 001, 002 and 017 are the ones with
real consequences. 013, 006 and 015 were cheap tidying, and all three are off
the list now, each ended a different way. 006 is done, and its
ruling was to delete both of the dead templates it names. The work in it was
not the deletion but the proof: a template can be reached by name from another
template rather than from Python, and the app-directory loader means a
same-named file in an installed package would decide which copy the loader
hands back, so both were checked before either was removed. It also left the
suite able to notice: nothing had pinned which template file the compact report
renders from, so the suite would have stayed green whichever of the two files
had been deleted. 013 is ``Fixed``: the five comments are gone, and the ruling
took option 2's browser test as well as option 1's deletion, since driving the
filter and the action in Chromium is what showed there was nothing behind them
-- and showed where the complaint came from, which is that Grappelli deletes
the admin's "Go" button and runs an action from the dropdown's ``change``
event. 015 is the one that ended in ``Rejected``: the mixed ``6em`` and
``2.0em`` is real and costs nothing, and the halves cannot be printed as
integers without moving the shadow, so the tidy version is floats everywhere
and reads worse than what is there. 014, the third of the ``Low`` three, is
``Deferred`` rather than closed: 034 settled what to do with it -- nothing,
until the file it lives in is deleted at upgrade Stage 5 -- and it was left
``Open``, which put a ruled-and-untouchable issue on :doc:`next`'s ready
queue. 016 and 018 are about
the future rather than today; 016 is fixed, since the construct that is correct
on both interpreters costs nothing to adopt now and Python 2's behaviour is
unchanged by it.

From the dependency upgrade analysis
------------------------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 019 High     settings / upgrade      Settings define no MIDDLEWARE
 020 Low      dependencies / cleanup  django-indexer and django-paging are unused
 021 Low      settings / dependencies gunicorn is an app for a removed command
 022 Low      urls / cleanup          Dead /media/grappelli/ route, ADMIN_MEDIA_PREFIX
 023 Medium   settings / upgrade      contrib.messages configured but not installed
 024 Medium   settings / py3          TEMPLATE_DIRS hardcodes a python2.7 path
 025 High     security / settings     SECRET_KEY and DB password are committed
 026 Medium   settings / deployment   ALLOWED_HOSTS is set nowhere in the repository
 027 High     dependencies / build    No upper bounds; --no-deps is load-bearing
 028 Medium   dependencies            photologue <=3.15.1 breaks on Pillow >=10
 029 Low      dependencies / build    gunicorn <=20.1.0 breaks on setuptools >=82
 030 Low      dependencies / build    django-sortedm2m <2 cannot be built by modern tools
 031 Medium   dependencies / build    Three dependencies installed from URLs, not PyPI
 032 Low      deployment / cleanup    fabfile.py duplicates the Ansible deployment
 033 Low      dependencies / cleanup  django-pserver is required but never used
 034 High     templatetags / upgrade  admin_list fork needs re-syncing 19 times
 035 Low      dependencies / arch     photologue and grappelli cap the Django version
 036 High     platform / security     The runtime stack is end-of-life and unpatched
==== ======== ======================= ==================================================

**036 is the umbrella** -- the Python 2.7 / Django 1.5 modernisation, planned in
``docs/upgrade-plan.rst``. Read it first; it lists which of the others block it.

Of the rest, 025 and 026 are security questions independent of the upgrade and
could be decided immediately. Both were, and both are ``Fixed`` in the same
sense: the repository stopped depending on something only the server had, and
the act that ends the problem is somewhere else. 026's ruling came from the
maintainer reading the server, and the answer was the bad one -- an untracked
``local_settings.py`` there sets ``DEBUG = True``, so both of the two cases the
issue offered were true at once, the second by way of the first. Its file
carries that output. What is left of each is on the server: 049 deploys the
rotated secrets, and 051 -- new, from 026 -- deletes that file, which can only
happen after 026's ``ALLOWED_HOSTS`` change is deployed. 019, 023 and 024 are
one-line defensive changes that are no-ops today and prevent silent breakage
later -- the cheapest things on this list. 019 is done: the Django 1.5 default middleware tuple is copied into
``common_settings`` verbatim, which changes nothing that runs today and gives
Stage 8 a list to rename instead of an absence to notice. It also finished half
of 023, since ``MessageMiddleware`` is in that default; the other half -- the
``INSTALLED_APPS`` entry -- followed the same day, so 023 is done too. 024 is
done as well, and was cheaper still: the ``site-packages`` path it names had
already stopped resolving in the container, so deleting it changed nothing
anybody could see, and photologue's templates go on coming from the app
template loader. All three of them are now off the list.
027 is the one with a real design decision in it, and it has been taken now
that 028, 029 and 030 -- the three constraints its lock had to record -- are
all settled. The decision splits the issue in two: the completeness is done
today, by hand, so ``requirements/production.txt`` names every runtime package
including Pillow and ``dev/Containerfile`` installs one file with one command;
the mechanism it proposed, ``uv pip compile`` from a ``*.in``, waits for the
Python 3 flip, because ``uv`` refuses Python 2.7 outright and its nearest
answer picks a Pillow that will not install here. The one surprise is in what
the file does *not* say: ``django-sortedm2m``, which the issue and the
container comment both called a photologue dependency, is not one until
photologue 2.8, so it left the image rather than joining the file.
034 wanted deciding before
the upgrade reached Stage 6 and has been: it is ``Fixed`` with no code change,
because what it asked for was a ruling. The ruling retires the ``admin_list``
fork rather than carrying it, and schedules the deletion for Stage 5 -- the
stage that installs the Django version, 1.7, in which Django closed the very
ticket the fork carries. Its file keeps the measurements that produced that
answer, including two things nobody had noticed: one of the three CSS rules the
fork exists to serve has never matched anything, and three more Django API
removals hide inside it. It is also why 014, the dead code in the same file,
is settled without being touched. 020, 021, 022, 032 and 033 are deletions, and
all five are done now, 022 and then 032 following the first three. The first
three went in
one change that took six lines out of two requirements files and one settings
module, together because two of them edit the same ``INSTALLED_APPS`` tuple and
all three share one verification. The only surprise was in 020:
``django-indexer`` does ship a model and a South migration, against what the
issue asserted, and its empty table stays in the production database beside the
sentry ones. 022 is the one of the four that had a ``Decision`` to make, and
its single option survived everything that could have overturned it: the
installed grappelli has no ``media/`` directory, nothing outside these
documents names either the route or ``ADMIN_MEDIA_PREFIX``, and a rendered
admin page serves all of its grappelli assets from ``STATIC_URL``. Its file
also corrects ``upgrade-plan.rst``'s count of the string views Django 1.10
rejects, which had not been recounted since 048 added one. 032 is the last of
the five, and the one whose deletion took a ruling rather than a check: the
file also described a second site, and what to do about that record was the
maintainer's to say, not a thing to infer from the tree. It was asked and
answered -- the deployment is not written down here, and the file in the
history is where it stays. 032 also
finished a third of 031: two of that issue's three URL dependencies went with
the things that wanted them, and ``django-jqm``, the only one in production,
was what it stayed open for. It is ``Fixed`` now too, and it is the one issue
here whose fix is a *copy*: the fork is six templates and two static files in
``jqm/``, taken at 1.1.0.2 with the URL and the date recorded beside them, and
nothing under ``requirements/`` names a URL any more. Its file says what was
left behind as well -- a seventh template for a page this site does not have,
and three ``startapp`` stubs -- and says the one thing vendoring did not fix:
these templates still fetch jQuery from a CDN when a browser renders them,
which is a page asset rather than a build input.


From the photo management walkthrough
-------------------------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 037 Medium   admin / usability       No in-UI instructions for managing plant photos
 039 Medium   views / labels API      The label photo is saved but never read back
 042 Medium   models / photos         A species photo cannot be replaced once set
==== ======== ======================= ==================================================

Read together with 002 and 003, which concern the same auto-attach signal: if
that behaviour changes, the instructions asked for here change with it. All
three are now ``Fixed``. 039 was the reason 037 had nothing honest to say about
choosing a photo, and having been fixed it is why the label editor can now say
the chevrons choose the photo for *that label*. 042 is the capability behind
037's missing instructions, and its sentence -- every save re-attaches, so the
workflow is "save the one you want last" -- is in the text 037 added. 037 also
took the half of the capability 042 left: a species' photo could be replaced
but not removed, so its own fix puts ``photo`` on the species form.


From the documentation work
---------------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 038 Low      documentation / tooling The repository has no rendered documentation
==== ======== ======================= ==================================================

**038** is the one issue on this page that was being acted on rather than
waiting for a decision when it was filed: it carries the design of the Sphinx
build in ``docs/``, including
which of its workarounds fall away at which stage of ``docs/upgrade-plan.rst``.
It is ``Fixed``, and the ruling it eventually needed was not about the build but
about the reader: where the rendered documentation should live, and whether
these pages should be published at all while the register names production
hostnames and three unremediated security issues. The answer to the second was
that the repository is already public, so a rendered site changes how easily
that is found and not whether it is disclosed. The first went to GitHub Pages
rather than Read the Docs, so that CI and a developer keep running the one same
command. Its remaining table rows are triggers that have not fired, all but two
of them Stage 10 of the upgrade plan.


From the dashboard walkthrough
------------------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 040 Medium   packaging / i18n        Django ships no translations, admin chrome English
 041 Medium   views / public site     Duplicate observation numbers crash the observation page
==== ======== ======================= ==================================================

Both were found by looking at the rendered admin front page while linking the
custom views from it. 040's fix is one step in each image definition, and it
changes how the application is built; measuring it also corrected the file,
since only the development image turned out to be affected. 041 was invisible
while the view it
concerns had no link; the link added by the same work is what exposed it, and
it needs a ruling on what a duplicate museum number means before it can be
fixed.


Reported by the maintainer
--------------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 043 Low      admin / photos          The photo changelist cannot be sorted by name
 044 High     dev environment         Large admin pages truncated for a remote browser
 045 Medium   templates / mobile      The label editor is unusable on an iPad
 046 Low      templates / labels UI   The label editor opens at print size
 047 Medium   templates / labels UI   The label print toggle uses a glyph no font has
 048 Medium   dev environment / media Dev photos were loaded from the production host
 049 High     deployment / security   Production still runs the old SECRET_KEY and DB password
 056 Medium   templates / mobile      iPad label text is doubled, and grows until it vanishes
==== ======== ======================= ==================================================

043-047 were split out of ``incoming.rst``, where they were written down as
they were noticed, and **056** was split out of it two days later, from the
same tablet and the same page: it was noticed while looking at what 045's cheap
half had done. It is the only one of these whose fix landed before it had a
number, so filing it was a verification first -- and it came apart into a half
that is fixed and pinned by the browser suite and a half that no browser on any
machine here can watch, which is why it is ``Accepted`` and says so at length.
048 and 049 were reported straight into a task and never
passed through it. **050** came out of settling 017 and is below them, and
**051** came out of settling 026 the same way -- from being told what is on the
server, which is the one thing neither issue could find out here. Unlike
the rest of this register 043-049 describe symptoms rather
than causes, so each says how far the cause was traced, and each was taken back
to the reporter once for the detail that could only come from the machine it
happens on. 049 is the exception to that as well as the newest: its cause is
known exactly, and what it is waiting for is a decision about *when*.

043 is fixed: it was one attribute, ``admin_order_field``, and the work was the
two sub-decisions around it -- which collation the databases sort under, and
that the ordering assumes one photo directory. 046
and 047 have their rulings recorded -- 50 % on screen with print unaffected,
and an inline SVG printer whose label toggles the checkbox. 045
has its scope: the admin works on the tablet, so the work is the label editor
and printing. Its cheap half -- the viewport tag, a print button and a print
toggle that needs no hover -- was done first, and its large half waited for
017, as it said it should: with a browser suite to catch a regression in it,
the drag-and-drop layer is now pointer events and a number can be moved by
finger. It is **fixed**, with the confirmations that need the actual iPad
listed in its file rather than asserted here. 044 turned out not to be an admin issue at all: the pages it names are
cut off mid-response before the submit row is reached, and the boundary is a
size, not a model. It is filed under the dev environment and is the one item on
this page that stops the maintainer working today. 048 is from the same pair of
machines and was the odd one out here: its cause was fully known and nothing in
it was a defect -- the development settings named the production media host on
purpose -- so what it asked for was a ruling on a design, not a repair. It got
one the day it was filed, and is **fixed**: the development server serves the
photos it has and redirects the rest to that host. 049 is the newest and the only
one here that is not about this repository at all: 025 took the production
secrets out of the tracked files and the maintainer rotated them into the vault,
but the server still runs the old ones, so the disclosure is live until a
playbook run makes the new values the ones in use. It sits here rather than
inside 025 because it is a separate act on a machine nothing here can reach, and
because the customer has to agree when to spend its cost -- one round of logouts
and any outstanding password-reset links. The typing, at least, is written down
now: 049, 050 and 051 are one sequence with a load-bearing order, and
``ansible/secure-production.yaml`` is that sequence, with its runbook in
``README.rst``. All three stay open, because what they are waiting for is the
ruling on *when*, not a way to do it.


From settling issue 017
-----------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 050 High     security / deployment   A production admin password is committed and in use
 053 Low      views / labels API      Museum numbers on a label come in any order
==== ======== ======================= ==================================================

The one issue here that was found by *deleting* something. 017's browser suite
logged into the admin with a username and password written into
``conftest.py``, and the password matched the production dump's hash for that
account exactly, so the file had been publishing a working superuser login
since 2020. 017 could take it out of the tracked files and nothing more, which
is 025's split repeated: the act that ends the disclosure is on the server, and
it is this issue. Two smaller findings came out of the same work and went to
:doc:`incoming` rather than here. One of them is now **053**: the museum
numbers on a label arrived in whatever order the ``Observation`` objects sat at
in memory, and it is ``Fixed``. The ruling it was waiting for turned out to be
about the nullable column rather than about the numbers -- no data anybody has
reaches that case -- and the maintainer gave it the same day it was asked for.
The other, a save that silently does nothing without an admin cookie, is still
in :doc:`incoming`.


From settling issue 026
-----------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 051 High     deployment / security   Production serves with DEBUG on, from an untracked file
==== ======== ======================= ==================================================

The third repetition of 025's split, and the only one where the server's copy of
something is what makes the site work at all: an untracked ``local_settings.py``
in the deployed package directory turns ``DEBUG`` on, which is why the missing
``ALLOWED_HOSTS`` never mattered. 026 could put ``ALLOWED_HOSTS`` in the tracked
settings and nothing more; deleting that file is this issue, and doing it before
026's change is deployed would 400 the site.


From covering issue 011
-----------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 054 Low      fixtures / public site  Species list names a photo size not in the fixtures
==== ======== ======================= ==================================================

The one issue found by writing a test that had to *arrange* the defect away
before it could test anything else: 011's coverage of the species list needed a
``mobilethumbnail`` ``PhotoSize`` that ``initial_data.json`` did not ship, and
the fixture that created it was the report. Unlike 050 and 051 above, the thing
only the server could answer -- whether production has the row -- did not need
the maintainer: the dump under ``.dev/backups/`` has the table, the row is in
it, and that closed the half of the issue that would have been a live defect.
It is the reverse of 025's split, in other words: everything left to do was in
this repository.


From running the suite in a second engine
-----------------------------------------

==== ======== ======================= ==================================================
  ID Severity Area                    Title
==== ======== ======================= ==================================================
 061 Medium   tests / browser engines Every Safari claim was checked in Chromium
 062 Medium   templates / labels UI   WebKit draws fitted label text at a 9px floor
==== ======== ======================= ==================================================

017's browser suite launched Chromium and nothing else, so the four iPad
reports -- 045, 046, 047 and 056 -- were all verified in the engine none of
them came from. **061** is that corrected: every test runs in Chromium and in
Playwright's WebKit, which is Safari's engine without iOS around it, and CI
runs one leg per engine. It is ``Fixed``, and the useful part of it is what the
second engine said. It agreed with every assertion the register rests on, and
it disagreed about two measurements no assertion was tight enough to notice.
One of those is **062**: inside 046's ``zoom: 0.5`` WebKit will not draw text
below nine used pixels, so a name fitted under 18px is drawn at 18px -- the
size fitty computes is not the size drawn, on the engine every report about
that page came from. 062 is a measurement waiting for a ruling between three
answers, and the one thing it cannot establish here is whether iOS Safari has
the same floor.


Already fixed
=============

Found by the same work and fixed as part of it, each with a regression test.
Listed here so the record is complete; no issue file was opened for them.

============================================= =========
Defect                                        Commit
============================================= =========
Admin Observation form crashed on an empty     b8ad488
database: ``get_next_observation_extid()``
indexed ``[0]`` into an empty queryset, and
NULL ids sort first on PostgreSQL
``Species.nicknames()`` called a manager       b8ad488
method that does not exist; dead and broken,
so removed
``PlantingAdmin.coordinates`` reused ``{0}``   c10a156
and ``{1}``, silently never showing width
and depth
``get_labels_data`` printed to stdout on       da7a076
every request
``media_root`` test fixture did not actually   1e3f7fb
redirect file storage, so uploads leaked
between tests
Grappelli 2.5 renders a ``<script>`` for      defdc28
``grappelli/jquery/i18n/ui.datepicker-fi.js``
on every admin page and ships only ``de``
and ``fr``, so the admin fetched a 404 per
page and every ``DateField``'s picker stayed
English. The file is in
``kasvimuseo/static/`` under grappelli's own
name now. Found by the browser suite's
``assert page.console_errors == []`` at
upgrade plan Stage 3, which is the only
check here that can see a 404 on a
subresource
``PhotoForm.clean()`` did not call             01db2fc
``super()``, and ``BaseModelForm.clean()``
is what switches ``validate_unique()`` on,
so a photo whose title was already taken
reached PostgreSQL: a 500 on the upload,
with the image file already written and no
row pointing at it
============================================= =========


Observations, not actionable
============================

Noted while testing; nothing to do, but worth knowing before someone
rediscovers them.

From the test coverage work
---------------------------

* **The admin login gate does not redirect.** Django 1.5 returns 200 rendering
  the login form at the requested URL rather than 302 to ``admin:login``. No
  data leaks. Later Django versions redirect.
* **``months.month_name`` returns a lazy translation proxy.** ``x in
  month_name(...)`` raises ``TypeError: coercing to Unicode``. Fine in
  templates, a trap for Python callers; force it with ``format()``.
* **``/photologue/`` answers 301**, not 302 -- it is a permanent
  ``RedirectView``.
* **Grappelli skips an empty dashboard module entirely**, so "Recent Actions"
  has no heading until a ``LogEntry`` exists.
* **``PhotoForm`` cannot be instantiated without a database.** Photologue's
  ``post_init`` receiver queries ``PhotoSize``, so even pure form tests need
  ``@pytest.mark.django_db``. ``PhotoSizeCache`` is a Borg whose state outlives
  the test transaction.
* **The repository's Python 3 lint hooks report false positives** on this
  Python 2.7 code -- unresolved imports for ``django``, ``photologue`` and
  ``south``, which only exist inside the dev container. ``ty.toml`` silences
  the import rules for this reason.

From the dependency upgrade analysis
------------------------------------

Suspected problems that turned out **not** to be problems. Recorded so nobody
spends time re-investigating them.

* **ExifRead is safe across its whole range.** photologue calls exactly one
  function, ``exifread.process_file``, and it is present and unchanged from
  2.1.2 through 3.5.1. The 2.x to 3.x major bump does not affect this project.
* **``Image.FLIP_LEFT_RIGHT`` and ``Image.ROTATE_180`` still work on Pillow
  12.** photologue uses both. Only ``Image.ANTIALIAS`` was removed -- see issue
  028.
* **pytz is safe.** Django 1.11 through 3.2 depend on it without an upper
  bound, but it is a data package with a stable API; a 2026 release works with
  Django 1.11.
* **sqlparse and asgiref are safe.** Django bounds them itself
  (``asgiref<4``, ``sqlparse>=0.3.1``), so they need no attention.
* **``pytest-django==2.9.1`` is good to Django 1.9**, not just 1.5. Its
  ``tox.ini`` lists Django 1.4 through 1.9. The comment in
  ``requirements/testing.txt`` -- "the last release supporting Django 1.5" --
  is true but reads as more limiting than it is: the test stack needs no
  attention for the first seven upgrade stages.
* **``grappelli.dashboard`` survives to grappelli 5.0.0.** It was worth
  checking, since ``ylaneenkasvit/dashboard.py`` depends on it and it is an
  optional sub-application.
* **``uv`` cannot target Python 2.7** (its floor is 3.6), so the early upgrade
  stages cannot be resolved with it and stay hand-maintained. Not a defect in
  anything, but it is the reason ``upgrade-plan.rst`` Appendix A starts at
  Stage 10.
