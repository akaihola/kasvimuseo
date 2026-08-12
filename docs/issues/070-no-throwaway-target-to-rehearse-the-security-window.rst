=============================================================================
Issue 070: No throwaway target to rehearse the security maintenance window
=============================================================================

:Status: Fixed
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
:Decision: Build the throwaway target, and run it before the real window. A
    faithful target exists and the compute is a few cents, so the obstacle is two
    setup acts, not money. The choice was between DigitalOcean's 4 USD Basic
    Droplet, at about 0.006 USD an hour, billed per second and inbound free, and
    Hetzner's CX22 at 5.49 EUR a month; the maintainer confirmed Hetzner on
    2026-08-08, whose 2 vCPU and 4 GB suit the PostgreSQL, uWSGI and nginx stack
    where the droplet's 1 vCPU and 512 MB would not. Rule out Cloudflare and
    Fly.io: neither gives
    an SSH-reachable systemd host that keeps what ``apt`` installs. Two
    preconditions the run cannot skip and inventory cannot supply. First, a
    Debian 10 or Ubuntu 18.04 image, because the playbook installs
    ``python-minimal`` and no provider still ships that release as stock -- the
    same end-of-life runtime issue 036 tracks. Second, a throwaway public DNS
    name the maintainer controls, pointed at the host, because the nginx template
    names a Let's Encrypt certificate per domain and the verify play checks HTTPS
    with a trusted certificate. If standing up staging DNS is not wanted, run the
    reduced rehearsal in "What we found" point 4: it still proves the ordering
    that makes 049 hard to take. It was recorded on the evidence, the way 031 is,
    because the investigation was complete and only the go-ahead remained, and
    this workflow does not guarantee a live answer; the go-ahead, and the Hetzner
    choice, then arrived.
:Resolution: The repository half is built. ``ansible/hosts.staging`` is a
    separate inventory the production ``hosts: all`` cannot reach, and
    ``ansible/vars/staging.yml`` overrides the three web-layer values -- the
    ``ALLOWED_HOSTS`` list, the nginx ``servers`` and ``certbot_certs`` -- as
    extra-vars, so a staging run points them at ``staging_domain`` while every
    other value comes from ``vars/main.yml`` unchanged and no production file
    moves. README.rst, "Rehearsing the window on a throwaway host", is the
    runbook, keyed to the Hetzner CX22. What remained was the follow-on act a
    checkout cannot do: stand up a host, point a throwaway DNS name at it,
    vault throwaway secrets, and run ``ansible/secure-production.yaml``
    against the staging inventory. On 2026-08-09 a first execution attempt
    fixed three faults in the prose before any server existed (commit
    1b93917). The runbook now bootstraps the fresh host, and plants the
    ``local_settings.py`` a fresh install does not have before a second run.
    The reduced variant now skips ``nginx,certbot,https`` and sets
    ``nginx_start=false``, instead of ``--skip-tags web``, which also skipped
    the uWSGI role and left 051's gate no ``uwsgi.ini`` to read. The verify
    play now also asserts the Strict-Transport-Security header (060). The
    maintainer then chose the reduced rehearsal now and the full one later,
    and it ran the same day: commit 8260b6f, on the idle Hetzner CX11
    ``lead-1``, wiped and booted from the archived Debian 10 cloud image in
    rescue mode. Two clean runs, with production's ``local_settings.py``
    shape planted between them, proved every claim under "What a rehearsal
    proves" except the two the web layer carries. The live run caught four
    more faults, each one live in the real window too. The install URL named
    the Bitbucket copy, which no longer receives pushes; a window run would
    have deployed stale code. ``bootstrap.yaml`` pinned Bitbucket's pre-2023
    ssh host key, which ssh refuses today. Nothing installed ``git``, which
    pip needs to clone the application. And the restore ran as ``postgres``,
    so a dump with no ``OWNER TO`` statements left the application locked
    out of its own tables. Commit 8260b6f fixes all four. The full rehearsal
    followed the same day, on ``kasvimuseo-staging.vempai.men``, and passed
    twice: commit a8df30b, ``ok=89 failed=0``, the second run quiet. Every
    claim under "What a rehearsal proves" now holds, the web layer included:
    the page answers 200 over a trusted certificate, the response carries
    ``Strict-Transport-Security`` (060), and a forged Host gets a clean 400.
    It caught three more faults. certbot writes one lineage per
    ``certbot_certs`` entry while the nginx template reads a directory per
    domain, so a three-name certificate left nginx unable to start; staging
    now issues one lineage per name, and production's ``live/`` layout must
    be checked before the window. Current master over the raw pre-South-cut
    dump answers 500, so the staging seed is now the migrated dump the
    README's "Crossing the South cut" section produces -- the real window
    has the same dependency. And the uWSGI role never started a stopped
    service; it does now. The staging host stays up for later use.

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

What we found
=============

The investigation asked four questions. Here are the answers, in order. They
carry the ruling in ``:Decision:``.

1. What the target must be
--------------------------

The target is a full Linux virtual machine with systemd and sshd, not a
serverless runtime. ``ansible/install.yaml`` runs ``apt`` and ``import_role``
for PostgreSQL, nginx and uWSGI; the verify play in
``ansible/secure-production.yaml`` reads ``/proc/PID/stat`` and calls
``systemctl show``. Two of the three named candidates fail that test:

- **Cloudflare runs no such host. Ruled out.** Workers are isolates with no
  operating system. Containers, at general availability since April 2026, are
  ephemeral OCI images a Worker starts on demand and that sleep on their own;
  ``wrangler containers ssh`` reaches one only while it runs, and does not wake
  a stopped one. Nothing there is a persistent, mutable, apt-managed host.
- **Fly.io runs the wrong kind of host.** A Fly Machine, and the Sprite built
  on it since January 2026, is a Firecracker microVM booted from your OCI image.
  Fly's own ``init`` is PID 1, not systemd, and ``fly ssh console`` is Fly's
  agent, not your sshd. Anything ``apt`` writes outside a mounted volume is
  undone on the next start, so the playbook's installs do not persist.

Only **Hetzner Cloud** and a **DigitalOcean droplet** give a real virtual
machine with systemd, sshd and a root filesystem that keeps what ``apt``
installs. One faithfulness limit binds both. The playbook installs
``python-minimal`` and runs ``/usr/bin/python2.7``, which exist only on Debian
10 or earlier and Ubuntu 18.04 or earlier. Neither provider still offers those
releases as a stock image; both retired them at end of life. So a faithful
rehearsal starts from a custom Debian 10 or Ubuntu 18.04 image you upload, or it
accepts a delta and installs Python 2.7 another way. This is the same
end-of-life runtime issue 036 tracks.

2. What it costs
----------------

The compute is a few cents. A DigitalOcean Basic Droplet is 4 USD a month, about
0.006 USD an hour, billed per second with a one-minute floor and capped at the
monthly price. A Hetzner CX22 is 5.49 EUR a month, about 0.0088 EUR an hour,
billed by the hour and capped at the monthly price; it carries 2 vCPU and 4 GB
against the droplet's 1 vCPU and 512 MB, so it suits the PostgreSQL, uWSGI and
nginx stack better. Charging stops only when you delete the server, not when you
power it off. The dump is ``.dev/backups/production.sql``, 17 MB; uploading it to
the host is inbound traffic, which both providers give free. So one short-lived
run costs under a euro, and the real price is the time to build the custom image
and to wire the DNS.

3. What the inventory needs
---------------------------

Three overrides are clean, one is a small refactor, and one part cannot come
from inventory at all.

- **Clean per-host overrides.** ``ansible/hosts`` names the staging host. A
  vaulted ``ansible/host_vars/<host>`` carries its own ``kasvimuseo_secret_key``,
  ``kasvimuseo_db_password`` and ``kasvimuseo_admin_passwords``. Use throwaway
  values, so no production secret reaches the host.
- **A small refactor.** ``kasvimuseo_allowed_hosts``, the nginx ``servers`` list
  and ``certbot_certs`` all sit in ``ansible/vars/main.yml``, which every host
  loads, and there is no ``group_vars``. To point them at staging without
  touching production, move them to ``host_vars`` or a staging vars file.
- **Cannot come from inventory.** The web layer is tied to a real domain.
  ``ansible/templates/nginx-site.conf.j2`` names
  ``/etc/letsencrypt/live/{{ server.domain }}/fullchain.pem`` for every server,
  and every server listens on 443 with TLS; the verify play requests ``https://``
  with certificate checking on. So the run needs a public DNS name the maintainer
  controls, pointed at the host, for certbot to issue a trusted certificate. A
  variable cannot supply that.
- **One more host requirement, not an override.** ``install.yaml`` installs the
  application from ``git+ssh://git@bitbucket.org/akaihola/kasvimuseo.git``, so
  the staging run needs the same Bitbucket access production has.

4. What a rehearsal proves, and what it does not
------------------------------------------------

It proves the run, seeded from ``.dev/backups/production.sql``:

- ``install.yaml`` completes in order, so 049's database and web tasks land
  together.
- 051's gate refuses to delete ``local_settings.py`` until the deployed settings
  read the environment and ``uwsgi.ini`` carries ``ALLOWED_HOSTS``, then deletes
  it and restarts uWSGI.
- 050's password script sets the vaulted passwords, is idempotent on a second
  run, and its audit lists the other accounts.
- The verify play's post-conditions hold: uWSGI started after its environment
  was written, no ``local_settings.py`` remains, and a forged Host header gets a
  400 and not a debug page.
- With the web layer up, nginx serves the ``Strict-Transport-Security`` header
  issue 060 adds.

It does not:

- end 049, 050, 051 or 060. Each lives on the real production process and its
  real nginx, and only the real run touches those.
- reproduce production's live session state: the forced logouts, and the cookies
  and reset tokens the running process still signs with the old key. A
  dump-seeded host has none.
- stand in for the real Let's Encrypt renewal of the ambitone.com names, or for
  production's exact operating system, unless the image matches it.

If staging DNS is not wanted, run the reduced rehearsal in README.rst, "Without
staging DNS". It keeps the uWSGI role, because 051's gate reads ``uwsgi.ini``,
and skips the nginx and certbot roles and the ``https``-tagged verify tasks.
That run still proves every ordering above except the nginx header, which is
most of what makes 049's timing hard to take.
