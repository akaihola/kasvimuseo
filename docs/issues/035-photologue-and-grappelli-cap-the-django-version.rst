=====================================================================
Issue 035: photologue and grappelli cap which Django can ever be used
=====================================================================

:Status: Open
:Severity: Low
:Area: dependencies / architecture
:Reported: 2026-07-28
:Source: Dependency upgrade analysis, branch ``requirements-update-plan``
:Evidence: (none)
:Depends on: (none)
:Blocks: (none)
:Related: 036 -- the ceiling that will make it recur
    028 -- the same two packages
:Decision: undecided
:Resolution: (none yet)

Problem
=======

Two dependencies pace the project's Django version, permanently and in both
directions.

**grappelli ships exactly one series per Django release.** From its own README,
which states the mapping for every version: 2.4.x is Django 1.4/1.5, 2.5.x is
1.6, 2.6.x is 1.7, and so on to 4.0.x for Django 5.x and 5.0.0 for Django 6.x.
There is no version of grappelli that spans two Django releases, so **no Django
version in the sequence can be skipped** without losing the admin -- which is
this application.

**photologue pins Django from above.** Verified by installing it: photologue
3.20 declares ``Django>=5.2,<6.1``.

The consequence is a ceiling on the future, not just a constraint on the
upgrade path. When Django 6.1 ships, this project cannot move to it until
photologue releases a compatible version. photologue is maintained by one
person and released roughly annually; grappelli likewise.

Impact
======

Low today -- both have current releases, and the upgrade plan reaches Django
6.0 with both satisfied. It is filed because it is the thing that determines
whether this situation recurs.

The reason this project is on Django 1.5 in 2026 is not that Django is hard to
upgrade. It is that every upgrade had to wait for two third-party packages, and
at some point the wait became permanent.

Options
=======

1. **Accept it** and track both upstreams. Reasonable: both are alive, and the
   admin skin and photo gallery are genuinely useful.
2. **Design out grappelli.** Django's own admin has improved considerably since
   1.5. The project uses grappelli for its appearance and for
   ``grappelli.dashboard``; the dashboard is the part with real content, and it
   is one file, ``ylaneenkasvit/dashboard.py``, 72 lines.
3. **Design out photologue.** Much harder -- it owns database tables and the
   photo-size machinery -- and probably not worth it.

Nothing needs deciding now. It is worth revisiting once the upgrade lands, when
the cost of the current arrangement is fresh.

See also
========

``docs/upgrade-plan.rst`` Parts 2.2 and 2.3.
