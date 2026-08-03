==============================================================================
Issue 060: nginx sends no ``Strict-Transport-Security`` header
==============================================================================

:Status: Accepted
:Severity: Medium
:Area: deployment / security
:Reported: 2026-08-02
:Source: Filed out of issue 059, which is the application half of the same
    window. Reading ``ansible/templates/nginx-site.conf.j2`` for the TLS
    configuration that made 059's ``SESSION_COOKIE_SECURE`` free showed that
    the header which would stop the cleartext request being made at all is not
    there
:Evidence: (no test) -- the header comes from nginx and nothing in this
    repository's suite exercises nginx, which is why the observation was
    ``grep -rn Strict-Transport ansible/`` returning nothing. The change was
    measured instead, outside the suite, and "Verification" below is the log:
    the template rendered with ``ansible/vars/main.yml``'s own variables;
    ``nginx -t`` on the rendering under nginx 1.30.3; that same rendering
    actually served, with ``curl`` reading ``Strict-Transport-Security:
    max-age=300`` off a 502 from the uWSGI location and a 404 from the static
    site, and off nothing at all on the port-80 redirect; and the same run
    repeated with ``always`` removed, which is what makes the header vanish
    from both. ``ansible-playbook --syntax-check`` passes on ``install.yaml``
    and ``secure-production.yaml``. ``--check`` was **not** run and cannot be
    from here: it stops at the vault password, and behind it is an SSH
    connection to the production host that this environment does not have.
    Nothing here observes the running server, so what the deploy does is
    inferred from the rendering, not seen
:Depends on: (none) -- but see ``Decision``: it is a change to the running
    server's configuration, so it lands on a deploy, like 049 and 051
:Blocks: (none)
:Related: 059 -- the application half, fixed. That change stops the first
    ``http://`` request leaking a session cookie; this one would stop the
    request being made
    049 -- the same repository-half / server-half split, and a playbook run this
    could ride
    051 -- likewise: a configuration change that only takes effect on a deploy
:Decision: **Send the header, staged: ``max-age=300`` now and ``max-age=31536000`` later, with neither ``includeSubDomains`` nor ``preload`` at either stage.** Ruled here, on the evidence, and not put to the maintainer -- which is the register's convention (003, 042, 049 all record a ruling taken from what could be read rather than waited for), and which is defensible in this issue only because of the shape of the ruling itself: the part that lands now is reversible in five minutes by construction, and every part that is not reversible is declined or deferred to a decision somebody still has to take on purpose. What made this a decision rather than a line of configuration is that ``max-age`` cannot be withdrawn faster than it expires, and the deployment reading in "The deployment, read" below is what settles the duration: three sites, one certificate covering all three names, renewed by a root cron job at 03:30 that stops nginx, renews and starts it again, whose failure output goes to cron's mail on the host -- which nothing in this repository configures, monitors or reads. An expired certificate is a warning a visitor clicks through today and a page no browser will open under a year-long promise, so a year cannot be the first value; but nothing in that argument survives five minutes, which is what the ``300`` stage costs to abandon. Hence stage 1, which the fix lands, and stage 2, which is a one-line commit against this issue once the conditions in "What has to be true before stage 2" are met -- among them that a renewal failure becomes visible to a person. Monitoring the renewal is a real defect and was considered for its own issue number; it is deliberately not filed as one, because at stage 1 the exposure it would cover is five minutes and because it is exactly the gate this issue is already held open by. Whoever files it can point at this field. ``includeSubDomains`` is declined rather than forgotten: each of the three names is a leaf, they are siblings rather than parents of one another, so none of them is covered by another's header in any case, and the directive would only commit names that do not exist yet and might not be this project's. ``preload`` is declined outright, and would be even at stage 2: it is irreversible in practice, it requires ``includeSubDomains``, and it is a promise about the whole of ``ambitone.com``, which this project does not own alone. The alternative rulings, both rejected: going straight to a year, which buys a header nobody would dare deploy on an unmonitored renewal, and doing nothing until renewal monitoring exists, which leaves the cleartext window open for the sake of a risk that five minutes bounds. ``Status`` is ``Accepted`` and not ``Fixed`` for a reason that is the same shape as 056's: half of this has landed and pins itself, and the other half -- the year -- is owed and has nothing here to track it if this issue closes
:Resolution: (none yet) -- stage 1 is committed, in 0baa1a6: the ``add_header`` in ``ansible/templates/nginx-site.conf.j2``, the argument in that template's Jinja comment, and the deploy step and its consequence in ``README.rst`` under "The security maintenance window". That is everything this repository can do to *stage 1*, and the header is real on the next ``install.yaml`` run and not before. This issue closes with stage 2 -- ``max-age=31536000`` in the same directive -- which is one line, is deliberately not in this commit, and has conditions written below

Problem
=======

``ansible/templates/nginx-site.conf.j2`` serves each site on ``listen 443 ssl``
with Let's Encrypt certificates and answers port 80 with nothing but
``return 301 https://{{ server.domain }}$request_uri``. What it never sends is
``Strict-Transport-Security``, so a browser is told the site prefers HTTPS only
by being redirected, one request at a time, for ever: every visit that starts
from a typed address, an old bookmark or an ``http://`` link makes a real
cleartext request to port 80 first, and only then learns better. Issue 059
removed what that request carries -- the session and CSRF cookies are now
``Secure``, so they are not attached to it -- but the request itself still
happens, it still names the host and the path, and it is still the point at
which somebody on the path can answer instead of nginx and serve a plausible
page over ``http://``. One ``add_header`` in that template would end it for
every browser that has visited once. What makes it a decision rather than a
line of configuration is that the header is a promise with a duration:
``max-age`` commits the domain to HTTPS for that long in every browser that has
seen it, and it cannot be withdrawn faster than it expires, so the certificate
renewal this deployment already depends on becomes load-bearing for the site
being reachable at all. Whether ``includeSubDomains`` and ``preload`` belong on
it is a further question about the whole of ``ambitone.com``, which is not this
project's to answer alone.


The deployment, read
====================

The duration is a question about this deployment, so the deployment was read
before anything was proposed.

**Three sites, one template, one certificate.** ``ansible/vars/main.yml``
renders ``nginx-site.conf.j2`` once, into ``/etc/nginx/conf.d/default.conf``,
for three servers: ``kasvit.ambitone.com`` (the application, over uWSGI, plus
``/favicon.ico``), ``static.kasvit.ambitone.com`` and
``media.kasvit.ambitone.com`` (both plain ``alias`` roots). Each gets a
``listen 443 ssl`` server and a port-80 server that does nothing but redirect.
One ``certbot_certs`` entry covers all three names, so the three sites live or
die together: there is one renewal to fail, not three.

**Renewal is automated.** ``certbot_auto_renew: true`` makes
``geerlingguy.certbot``'s ``renew-cron.yml`` install a root cron job at 03:30::

    certbot renew --pre-hook "systemctl stop nginx" --post-hook "systemctl start nginx"

Standalone renewal, so nginx is stopped for it and started after it.

**Renewal is not monitored.** That is the crux, and it is worth saying flatly.
Nothing in this repository looks at whether that job succeeded. Its output goes
where cron sends output -- mail to ``root`` on the host -- and nothing here
configures an MTA, an alias for that mailbox, or any check that reads it. The
playbook's verification play (``-t verify``) asserts a great deal about issues
049, 050 and 051 and nothing about a certificate. So the failure mode is
silent: the cron job fails, nobody hears, and the first symptom is the site
going bad thirty days later. Today that symptom is a certificate warning a
visitor can click through -- ugly, survivable, and *noticed*. Under a year-long
``Strict-Transport-Security`` it is a connection the browser refuses to make,
with no click-through, for every visitor who has been to the site before, and
it stays that way until the certificate is fixed. That asymmetry is the whole
argument for staging rather than for a year, and it is why "make the renewal
visible" is a condition on stage 2 below rather than a nice thing to have.


The two stages
==============

**Stage 1, landed:** ``add_header Strict-Transport-Security "max-age=300"
always;`` on each of the three TLS servers, and on none of the port-80 servers.
Five minutes is the conventional "we can back out of this" value: a browser
that has seen it refuses ``http://`` for this host for five minutes, so
withdrawing the promise costs one playbook run plus five minutes of patience,
and the header itself is deleted by deleting one line. What it buys in the
meantime is small but real -- a browser that has just been to the site does not
make the cleartext request again -- and what it is really for is proof: a
deploy at this value exercises exactly the same code path a year does.

**Stage 2, owed:** the same directive with ``max-age=31536000``. A year is the
usual target because it is what makes the promise worth having: the visitor who
comes back next season is the one whose typed ``kasvit.ambitone.com`` still
goes straight to HTTPS. It is a one-line commit, and it belongs to this issue,
which is why this issue is not closed by the commit that lands stage 1.

The deployed configuration says which stage it is on, in a comment beside the
directive, so nobody has to infer it from a number.


What has to be true before stage 2
==================================

Written here so that whoever advances the value is checking something rather
than deciding it again.

#. **A deploy has carried stage 1**, so the directive has been rendered and
   reloaded by the real nginx on the real host at least once.
#. **All three names answer over HTTPS with the header**, read from outside::

       curl -sI https://kasvit.ambitone.com/ | grep -i strict-transport
       curl -sI https://static.kasvit.ambitone.com/ | grep -i strict-transport
       curl -sI https://media.kasvit.ambitone.com/ | grep -i strict-transport

   Three ``max-age=300`` lines. A missing one means a site that would have
   broken under a year.
#. **Nothing the site needs is served over plain HTTP.** Under stage 1 that
   would show up as an occasional broken image or script for a returning
   visitor; under stage 2 it is permanent. The pages are already served from
   the three HTTPS names, and issue 031 recorded the one known outbound plain
   fetch -- the vendored jQuery Mobile templates fetch jQuery from a CDN --
   which is a third-party ``https://`` URL and is unaffected by this header,
   but it is the class of thing to look for.
#. **A failed renewal reaches a person.** Anything counts: mail from cron that
   is actually delivered and read, an external certificate-expiry check, or a
   line in the verification play that asserts ``notAfter`` is more than a
   fortnight away. This is the one condition that is not a check but a piece of
   work, and it is the reason this issue is held open rather than closed with a
   short value shipped and forgotten.

None of these needs the maintainer's ruling. They need a deploy, which is
somebody's afternoon.


``includeSubDomains`` and ``preload``
=====================================

Both declined, explicitly.

``includeSubDomains`` extends the promise to every name *below* the one that
sent the header. The three names here are siblings, not ancestors:
``static.kasvit.ambitone.com`` is not underneath ``kasvit.ambitone.com``, so
none of them can cover another, and there is no fourth name under any of them
in ``vars/main.yml`` or anywhere else this repository can see. So the directive
would buy nothing today, and what it would cost is a commitment about names
that do not exist yet -- including any that somebody else in ``ambitone.com``
might one day put under one of these. It stays off at stage 2 as well, unless
somebody first establishes that there is nothing under those names and nothing
planned.

``preload`` is refused on different grounds: it is not a header directive that
does anything by itself but a request to be baked into browsers' shipped
preload lists, and removal from those lists takes months and a browser release
cycle even after the header changes. It also requires ``includeSubDomains``,
and the submission is naturally made for the parent domain. ``ambitone.com``
carries other things than this garden's plant museum, and this project is in no
position to promise HTTPS on their behalf. This is not a "not yet"; it is a
"not by this repository".


Verification
============

What was actually run, on a machine with no nginx, no Ansible and no route to
the production host -- so everything below is about the rendering, not about
the running site.

The template was rendered with the project's own variables (``jinja2`` over
``ansible/vars/main.yml``, the same ``item`` mapping ``nginxinc.nginx`` passes
it) and the result read: three TLS servers each carrying the header once, three
port-80 servers carrying none, and the long argument in the Jinja comment
appearing in no rendered file, which is why it is a Jinja comment rather than
three copies of itself in ``/etc/nginx/conf.d/default.conf``.

That rendering was then checked and served by a real nginx (1.30.3, from
``nix-shell -p nginx``), with five substitutions and nothing else changed: the
Let's Encrypt certificate paths pointed at a self-signed pair, the
``uwsgi_params`` include pointed at an empty file, and the two ports moved
above 1024 so an unprivileged process could bind them::

    nginx: the configuration file .../nginx.conf syntax is ok
    nginx: configuration file .../nginx.conf test is successful

Served, with the uWSGI socket deliberately absent so the application location
answers 502::

    $ curl -skI https://kasvit.ambitone.com:18443/          # the uWSGI location
    HTTP/1.1 502 Bad Gateway
    Strict-Transport-Security: max-age=300

    $ curl -skI https://static.kasvit.ambitone.com:18443/nothing
    HTTP/1.1 404 Not Found
    Strict-Transport-Security: max-age=300

    $ curl -sI http://kasvit.ambitone.com:18080/species/    # the redirect
    HTTP/1.1 301 Moved Permanently
    Location: https://kasvit.ambitone.com/species/
                                            # and no Strict-Transport-Security

Three things are pinned by that. The header reaches responses produced *inside*
the ``location`` blocks, so the inheritance nginx would have dropped had any of
those blocks added a header of its own is not being relied on blindly -- none
of them adds one, and the template says what to do if one ever does. The
port-80 server sends nothing, which is deliberate: a browser must ignore the
header on a cleartext response anyway. And both of those responses are error
responses, which is what ``always`` is for -- the same run with ``always``
removed returns the same 502 with no ``Strict-Transport-Security`` line at all.
A 502 is precisely the moment (uWSGI restarting during a deploy) at which a
browser should stay pinned.

Ansible was checked as far as it can be checked here::

    $ ansible-playbook --syntax-check ansible/install.yaml ansible/secure-production.yaml
    playbook: ansible/install.yaml
    playbook: ansible/secure-production.yaml

-- with an inventory of one made-up host, because the real one's ``host_vars``
file is vaulted and the vault password is not in this environment. The only
messages are deprecation warnings from the vendored ``nginxinc.nginx`` role,
which predate this change.


What could not be verified here
===============================

* **The deploy.** ``ansible-playbook --check`` was not run: it stops at the
  vault password before it reaches a connection, and behind that is SSH to
  ``vps763955.ovh.net``, which this environment has no route to. So "nginx
  reloads cleanly with this in place" is an inference from ``nginx -t`` on the
  rendering, not an observation.
* **The real certificate chain.** The served check used a self-signed pair;
  nothing here can see whether ``/etc/letsencrypt/live/`` on the host holds
  what the template names.
* **Whether the renewal cron has ever failed.** Its history is the host's mail
  spool, which nothing here reads. The statement above is that failure is
  *unmonitored*, which follows from the configuration; it is not a claim that
  it has or has not happened.
* **The suite says nothing about any of this.** ``dev/kasvimuseo app test``
  passes, unchanged, which is a statement that this change touches no Python
  and not evidence about the header.
