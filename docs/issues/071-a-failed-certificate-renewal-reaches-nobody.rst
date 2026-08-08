==============================================================================
Issue 071: A failed certificate renewal reaches nobody
==============================================================================

:Status: Fixed
:Severity: Medium
:Area: deployment / security
:Reported: 2026-08-08
:Source: Issue 060's ``Decision`` field, which read the renewal cron while
    ruling on the ``Strict-Transport-Security`` duration, called the missing
    monitoring "a real defect", declined to file it -- because at
    ``max-age=300`` the exposure it covers is five minutes -- and said
    "whoever files it can point at this field". This is that filing
:Evidence: (no test) -- the renewal runs on the production host and nothing in
    this repository's suite reaches Ansible, nginx or that host, so there is no
    behaviour here a test can pin. The observation is three readings of the
    configuration instead. ``ansible/vars/main.yml`` sets
    ``certbot_auto_renew: true`` with a 03:30 hour and the ``--pre-hook`` and
    ``--post-hook`` that stop and start nginx;
    ``ansible/roles/geerlingguy.certbot/tasks/renew-cron.yml`` turns that into
    a root ``cron`` entry and sets no ``MAILTO``; and
    ``grep -rniE 'postfix|msmtp|sendmail|exim|mailutils|MAILTO' ansible/``
    returns nothing, which is the same reading issue 066 made and had ruled on.
    What is pinned now is the fix: the assertion added to the verification play
    was rehearsed against two certificates, and "Verification" below is the log
:Depends on: (none) -- the play it lands in,
    ``ansible/secure-production.yaml``, exists already
:Blocks: 060 -- its stage 2, ``max-age=31536000``, is held on four conditions,
    and the fourth is this work: "a failed renewal reaches a person". The other
    three are checks somebody makes on a deployed stage 1
:Related: 066 -- the same missing mail transfer agent, read from the
    application's end. Its ruling is why cron's mailbox is not the answer here:
    the maintainer chose a log file over a daemon nobody runs, so mail on that
    host stays undeliverable on purpose
    070 -- the throwaway staging host. It is where this assertion can be
    exercised for real before the production window opens
    049 -- the playbook run this rides on, and the runbook in ``README.rst``
    under "The security maintenance window"
:Decision: **Assert the expiry in the verification play, and monitor nothing
    else.** Ruled here, on the evidence, and not put to the maintainer -- the
    register's convention when the work is complete except for a ruling (031 is
    the shape), and the cheap answer in this case, because issue 066 already
    carries the maintainer's ruling on the neighbouring question. Issue 060
    offered three ways to make a failed renewal visible: cron's mail actually
    delivered and read, an external certificate-expiry check, or an assertion in
    the play. Take the third. Mail is ruled out by 066: nothing on the host can
    deliver it, the maintainer decided a daemon is not worth running for
    ``mail_admins``, and the same argument holds for cron. An external check is
    the only one of the three that watches the site while nobody is looking, and
    it is also the only one that is not this repository's to install: it is an
    account somewhere, paid for or free, that nothing in a checkout can create
    or verify. The assertion is what a checkout can build, it runs where
    everything else about this deployment is already checked, and it costs one
    read of a file. What it buys is bounded and this issue says so under "What
    this does not do": it reports at the moment somebody runs it, so the person
    it reaches is the person already looking. That is enough for 060's stage 2,
    which needs the failure to stop being *silent*, and it is not enough to be
    called monitoring. A second, external watch stays worth having, and it is
    left as the follow-on below rather than pretended away
:Resolution: (none yet) -- to be filled in with the commit on this branch

Problem
=======

The Let's Encrypt certificate for the three names this deployment serves is
renewed by a root cron job at 03:30::

    certbot renew --pre-hook "systemctl stop nginx" --post-hook "systemctl start nginx"

``certbot`` renews a certificate once it has less than 30 days left, so the job
does nothing on most nights. When it does try and fails -- a rate limit, a
firewall, an nginx that does not come back up, a disk that is full -- it writes
the reason to standard error, and ``cron`` mails that to ``root`` on the host.
Nothing configures a mail transfer agent there, nothing aliases that mailbox,
and nothing reads it. So the failure is silent, and it stays silent for about
two weeks of nightly retries, until the certificate expires and the site starts
serving a certificate warning.

One ``certbot_certs`` entry covers all three names, so there is one renewal to
fail rather than three, and all three sites fail together.

Why it is worth fixing now
==========================

Today an expired certificate is a warning a visitor can click through: ugly,
survivable, and *noticed* -- somebody tells the maintainer. Issue 060 takes
that property away. Its stage 2 sends
``Strict-Transport-Security: max-age=31536000``, and a browser that has seen
that header refuses an expired certificate with no way to click through, for
every visitor who has been to the site before, until somebody fixes it. So 060
holds its stage 2 open until a failed renewal reaches a person, and this issue
is that condition.

What we did
===========

``ansible/secure-production.yaml``'s verification play reads the certificate
that nginx serves for each of the three names and fails when it has less than a
fortnight to run. Two tasks, at the end of the play, in the same style as the
post-conditions it already asserts for issues 049, 050 and 051::

    ansible-playbook ansible/secure-production.yaml -t verify

Three choices inside it are worth writing down.

**openssl, not** ``community.crypto``. ``x509_certificate_info`` is the
declarative way to read a certificate and it needs the ``cryptography`` library
under the interpreter Ansible uses *on the host*. Nothing in this repository
installs that library, this environment cannot look at the host to find out
whether it is there, and the host is the end-of-life Debian issue 036 tracks.
The ``openssl`` binary is there because certbot is there. ``openssl x509
-checkend`` answers the question directly -- it exits non-zero when the
certificate expires within the given number of seconds -- so no date is parsed
in Jinja and no collection is added to a repository that vendors its roles.

**A fortnight, named once.** ``certificate_expiry_margin_days: 14`` is in
``ansible/vars/main.yml``, beside the renewal cron it is about. certbot starts
renewing at 30 days and tries every night, so fourteen days is about fifteen
failed attempts: late enough that one bad night is not an alarm, early enough
that a person still has two weeks to act.

**One reading per name, over the paths nginx names.** The template names
``/etc/letsencrypt/live/{{ server.domain }}/fullchain.pem`` for each of the
three servers it renders, so the check reads those three paths and not the one
``certbot_certs`` entry. That is deliberate, and it is the one thing here that
could report something nobody expects: ``geerlingguy.certbot`` creates a single
lineage named after the *first* domain in the list, which is
``media.kasvit.ambitone.com``, while the template expects a directory per name.
Three directories therefore exist on the host by some route this repository does
not describe -- nginx would refuse to start otherwise -- and this check reads
each of them. A name whose file is missing, or which is a certificate nobody
renews, fails here rather than in a visitor's browser.

What this does not do
=====================

It is a check, not a monitor, and the difference matters.

* **It reports when somebody runs it.** Nothing runs the play on a schedule.
  So this turns a failure that was invisible into a failure that anybody
  verifying the deployment sees, and it does not wake anybody at 04:00.
* **It reads the file, not the served connection.** A renewal that writes a new
  certificate but leaves nginx serving the old one would pass. The renewal's
  ``--post-hook`` starts nginx, so that state is not the expected one; a check
  that opens a TLS connection to each name would cover it as well.
* **The read stops at the first name that fails.** Ansible ends the loop on the
  first failing item, so a run repaired one name at a time reports one name at
  a time. Run it again after each repair.

An external certificate-expiry check -- the second of the three routes issue 060
offered -- covers all three of those and is somebody's account rather than a
file in this repository. It stays worth having, and this issue does not claim
to have made it unnecessary.

Verification
============

What was actually run, on a machine with no route to the production host, no
vault password and no nginx -- so this is about the tasks, not about the
deployment.

The two tasks were copied into a small playbook, with the certificate path
pointed at a temporary directory and ``become`` removed, and run against
``localhost`` with ``ansible-core 2.21.2``. Two self-signed certificates stood
in for the real one: one with 90 days to run and one with 10.

The 90-day name passed and the 10-day name failed, with the message the task
sends::

    TASK [Read how much life each name's certificate has left] ****
    ok: [localhost] => (item=a.example.com)
    ok: [localhost] => (item=b.example.com)

    TASK [Every name's certificate outlives the renewal window (071, 060)] ****
    ok: [localhost] => (item=a.example.com)
    [ERROR]: Task failed: Action failed: The certificate nginx serves for
    b.example.com expires Aug 18 09:11:59 2026 GMT, which is less than 14 days
    away. certbot starts renewing at 30 days and tries every night, so the
    renewal has been failing for about a fortnight. ...

The missing-file case was run as well, by renaming one of the two certificates
away. The read task fails, and names the file::

    Could not open file or uri for loading certificate from
    .../a.example.com.pem: No such file or directory

The playbooks were syntax-checked as far as they can be checked here::

    $ ansible-playbook --syntax-check ansible/install.yaml ansible/secure-production.yaml
    playbook: ansible/install.yaml
    playbook: ansible/secure-production.yaml

-- with an inventory of one made-up host, because the real host's ``host_vars``
file is vaulted and the vault password is not in this environment. The only
messages are the deprecation warnings from the vendored ``nginxinc.nginx`` role,
which predate this change. ``ansible-core`` is not installed on this machine
either; the runs above used ``uvx --from ansible ansible-playbook``, and
``ansible-core`` 2.21.2 is what that installs today. The repository pins no
Ansible version, which is one more reason the check uses no collection.

What could not be verified here
===============================

* **The certificate on the host.** Nothing here can see
  ``/etc/letsencrypt/live/``, so "three lineages exist, one per name" is an
  inference from nginx starting at all, not an observation. The first run of
  ``-t verify`` on the real host is what settles it, and it settles it loudly.
* **The deploy.** ``ansible-playbook --check`` was not run: it stops at the
  vault password, and behind that is SSH to ``vps763955.ovh.net``, which this
  environment has no route to. This is the same limit issue 060 records.
* **Whether the renewal has ever failed.** Its history is the host's mail
  spool, which nothing here reads. The claim above is that a failure is
  *unmonitored*, which follows from the configuration; it is not a claim about
  what has happened.
* **The suite says nothing about any of this.** This change touches no Python.
