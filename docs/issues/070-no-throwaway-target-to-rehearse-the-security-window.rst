=============================================================================
Issue 070: No throwaway target to rehearse the security maintenance window
=============================================================================

:Status: Open
:Severity: Low
:Area: deployment / infrastructure
:Reported: 2026-08-06
:Source: Maintainer, asking whether a short-lived staging deploy can stand in
    for the production access that 049, 051 and 060 need
:Evidence: (none) -- this is an investigation, not a defect. There is no
    behaviour in this repository to pin; the question is whether a throwaway
    deploy target can be stood up, and at what cost
:Depends on: (none) -- the playbook it would exercise,
    ``ansible/secure-production.yaml``, exists already, so this can start now
:Blocks: (none) -- the real maintenance window can run without it; a rehearsal
    de-risks that window rather than gating it
:Related: 049 -- deploys the rotated ``SECRET_KEY`` and database password;
    the ordering a rehearsal would check is in its "What it takes" section
    050 -- rotates the committed admin password in the same sequence
    051 -- deletes the untracked ``local_settings.py``, after 026's
    ``ALLOWED_HOSTS`` change, which a rehearsal must prove does not 400 the site
    060 -- adds the ``Strict-Transport-Security`` header to nginx, which a
    rehearsal can confirm is served
:Decision: undecided -- whether to build a throwaway staging target at all, and
    which of the three candidates fits, is the maintainer's to rule once the
    investigation says what each costs and what each can host.
:Resolution: (none yet)

Problem
=======

Four items on this register are acts on the running production server, not
changes to this repository: 049 deploys the rotated secrets, 050 rotates the
admin password, 051 deletes an untracked settings file, and 060 turns on an
nginx header. No agent working from this checkout can reach that server, so all
four wait for a maintenance window that only the maintainer can open.

``ansible/secure-production.yaml`` carries out all four in the one safe order,
and ``README.rst`` documents the window under "The security maintenance
window". Today that playbook has exactly one place it can run: production. An
agent here cannot run it at all, so nobody finds out it works until the real
window is open and the customer is already paying the cost of it -- one round of
logouts, and a short outage while uWSGI restarts.

The maintainer asks whether a short-lived staging deploy could stand in. A
*staging deploy* is a throwaway Linux host that Ansible installs the application
onto exactly as it installs production, kept only long enough to run the
playbook against it, then destroyed. Three candidates are named: Cloudflare,
Fly.io Sprites, and a short-lived cloud server such as a Hetzner or DigitalOcean
instance billed by the hour.

Impact
======

A rehearsal cannot end any of the four disclosures. Each of those lives on the
real production process and its real nginx, and only the real playbook run
touches those. So a staging deploy does not close 049, 050, 051 or 060, and
this issue is not a substitute for the window they wait on.

What it would buy is the one thing missing from that window today: proof, before
it opens, that the playbook does what its files claim. The run is not trivial to
get right. 049 must land its database and web tasks together or the site breaks
until the second one runs. 051 must delete ``local_settings.py`` only after
026's ``ALLOWED_HOSTS`` change is deployed, or the site 400s. 050 changes a
password the application also uses. A rehearsal that runs the whole sequence
against a throwaway host, seeded from the dump under ``.dev/backups/``, would
turn each of those "must" clauses from a claim in a file into a checked fact --
which is most of what makes the "when" decision in 049 hard to take.

What to find out
================

The work is an investigation, and it ends in a ruling the maintainer takes on
the evidence. Answer these, in order:

1. **What the target must be.** The playbook installs PostgreSQL, uWSGI and
   nginx onto an SSH-reachable Linux host, and its post-conditions read files on
   that host. So the target is a full Linux virtual machine, not a serverless
   runtime. Check each candidate against that: Cloudflare's Workers and Pages do
   not run a VM Ansible can target, so name what part of Cloudflare could, or
   rule it out; confirm whether Fly.io Sprites and an hourly cloud server each
   give an SSH-reachable host whose OS and PostgreSQL version match production
   closely enough for the rehearsal to be faithful.
2. **What it costs.** Price the cheapest candidate for one short-lived run:
   the instance by the hour, and any egress for the dump.
3. **What the inventory needs.** Read ``ansible/`` and find every place a role
   or variable assumes the production host -- a hostname, a DNS name, a
   certificate. List what a staging inventory would have to override, and
   whether any of it cannot be overridden.
4. **What a rehearsal proves, and what it does not.** Write it down plainly, so
   the rehearsal is never mistaken for the fix: it proves the run's ordering and
   post-conditions; it does not end a disclosure and it does not reproduce
   production's live session state.

Record the answers in ``:Decision:`` with the ruling, the way 031 does. If the
answer is that no candidate is cheap enough or faithful enough to be worth it,
that is a valid ruling and closes the issue ``Rejected`` with the numbers that
made the case.
