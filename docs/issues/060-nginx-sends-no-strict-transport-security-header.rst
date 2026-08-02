==============================================================================
Issue 060: nginx sends no ``Strict-Transport-Security`` header
==============================================================================

:Status: Open
:Severity: Medium
:Area: deployment / security
:Reported: 2026-08-02
:Source: Filed out of issue 059, which is the application half of the same
    window. Reading ``ansible/templates/nginx-site.conf.j2`` for the TLS
    configuration that made 059's ``SESSION_COOKIE_SECURE`` free showed that
    the header which would stop the cleartext request being made at all is not
    there
:Evidence: (none) -- there is no test, and this repository has no way to write
    one: the header would come from nginx, and nothing here exercises nginx.
    ``grep -rn Strict-Transport ansible/`` returns nothing, which is the whole
    of the observation
:Depends on: (none) -- but see ``Decision``: it is a change to the running
    server's configuration, so it lands on a deploy, like 049 and 051
:Blocks: (none)
:Related: 059 -- the application half, fixed. That change stops the first
    ``http://`` request leaking a session cookie; this one would stop the
    request being made
    049 -- the same repository-half / server-half split, and a playbook run this
    could ride
    051 -- likewise: a configuration change that only takes effect on a deploy
:Decision: undecided
:Resolution: (none)

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
