==============================================================================
Issue 059: Cookies are not ``Secure``, and no page refuses to be framed
==============================================================================

:Status: Fixed
:Severity: High
:Area: settings / security
:Reported: 2026-08-02
:Source: Reading ``ylaneenkasvit/common_settings.py`` beside
    ``ansible/templates/nginx-site.conf.j2`` after issue 057 landed. The
    deployment is TLS-only and the settings are written as if it were not:
    ``grep -rn 'SESSION_COOKIE_SECURE\|CSRF_COOKIE_SECURE\|X_FRAME_OPTIONS'``
    over every settings module returned nothing
:Evidence: kasvimuseo/tests/test_settings_cookie_security.py -- sixteen tests,
    of which twelve failed before the change, and the four that did not are
    named in "Verification" with what they are for. The behavioural ones log in
    and read the ``Secure`` attribute off the cookie the login actually issued,
    and read ``X-Frame-Options`` off the admin's and the label editor's
    responses. Measured before the change through the running server as well:
    ``curl -i`` on a login over ``dev/kasvimuseo app run`` returned
    ``Set-Cookie: sessionid=...; httponly; Path=/`` -- no ``secure`` -- and no
    ``X-Frame-Options`` on any response.
    ``kasvimuseo/tests/test_settings_middleware.py`` is the test issue 019 left
    behind, and it is changed deliberately here rather than loosened: it now
    expects the Django 1.5 default *plus* the one entry this issue adds
:Depends on: (none) -- three settings and one middleware entry in a file this
    repository owns. It is deliberately **not** ordered behind 049 or 051:
    neither the cleartext window nor the framing depends on which key is in use
    or on whether ``DEBUG`` is off
:Blocks: (none)
:Related: 057 -- the same file, the same class of defect and the shape this
    issue is argued in: a Django 1.5 default that is wrong for this deployment
    and that the upgrade would only reach much later
    025 -- where the disclosure that makes a leaked session cookie worth having
    is described; a cookie sent in cleartext is one more way to the same place
    049 -- the half of 025 that is still open on the server. Its playbook,
    ``ansible/secure-production.yaml``, is the maintenance window this change
    can ride, because it logs everyone out anyway
    051 -- the other repository-half / server-half split of the same shape: the
    repository can only set what the next deploy will read
    019 -- why ``MIDDLEWARE_CLASSES`` is written out at all, and the test that
    pins it. This is the first entry deliberately added to that list, which
    that issue anticipated
:Decision: Take all three settings now, in ``ylaneenkasvit/common_settings.py``, and leave ``CSRF_COOKIE_HTTPONLY`` alone with the reason written beside it. Four things settled it. The deployment has been TLS-only since Let's Encrypt was wired into ``nginx-site.conf.j2``, so ``SESSION_COOKIE_SECURE`` and ``CSRF_COOKIE_SECURE`` cost this site nothing and are only ``False`` because Django 1.5 has to default them that way for sites that are not. ``XFrameOptionsMiddleware`` is one list entry, and the alternative -- a ``X-Frame-Options`` header from nginx -- would put a Django concern on the server half, where 049 and 051 show how long a change can sit. ``X_FRAME_OPTIONS`` is written out at ``SAMEORIGIN`` although that is also the 1.5 default, for the reason 019 gives about ``MIDDLEWARE_CLASSES``: the default is not stable, Django 3.0 changes it to ``DENY``, and an upgrade should not deliver that as a surprise. ``DENY`` was considered and rejected: the attack is a foreign page framing this one, which ``SAMEORIGIN`` refuses, and ``DENY`` additionally refuses this site framing itself -- no security, and the installed grappelli ships TinyMCE, whose editor is an iframe. ``CSRF_COOKIE_HTTPONLY`` is the one deliberately left alone, and it has a section of its own below. The alternative considered for all of it -- wait, and let the upgrade bring better defaults -- was rejected because none of these is a default in any Django version the plan reaches: they are all still off in Django 5, because they are properties of the deployment, not of the framework.
:Resolution: 81fe7d1 -- ``SESSION_COOKIE_SECURE``, ``CSRF_COOKIE_SECURE``, ``X_FRAME_OPTIONS`` and ``XFrameOptionsMiddleware`` in ``common_settings.py`` with the reasons beside them; the plain-HTTP overrides in ``test_settings.py`` and ``local_settings.development.py``; ``xframe_options_exempt`` on the two embedded reports in ``kasvimuseo/urls.py``; and ``kasvimuseo/tests/test_settings_cookie_security.py``. ``CSRF_COOKIE_HTTPONLY`` is not set, deliberately, and the test that will notice when the upgrade makes that a live question is in the same file. The server-side complement is 060, filed separately and still open.

Problem
=======

No settings module in this repository set ``SESSION_COOKIE_SECURE``,
``CSRF_COOKIE_SECURE`` or ``X_FRAME_OPTIONS``, and ``MIDDLEWARE_CLASSES``
carried no ``XFrameOptionsMiddleware``::

    $ grep -rn 'COOKIE_SECURE\|X_FRAME_OPTIONS\|clickjacking' ylaneenkasvit/*.py
    $                                       # nothing, before this change

So the installed Django's defaults applied. Read from the container rather than
from memory::

    >>> import django; django.get_version()
    '1.5.12'
    >>> from django.conf import global_settings
    >>> global_settings.SESSION_COOKIE_SECURE, global_settings.CSRF_COOKIE_SECURE
    (False, False)
    >>> global_settings.X_FRAME_OPTIONS
    'SAMEORIGIN'

``X_FRAME_OPTIONS`` has a default and it is the safe one -- but nothing reads it
without the middleware, so it was inert.

Measured through the running server, before the change, with
``dev/kasvimuseo app run`` and ``curl -i``::

    Set-Cookie: csrftoken=Fwjh...; expires=...; Max-Age=31449600; Path=/
    Set-Cookie: sessionid=cvml...; expires=...; httponly; Max-Age=1209600; Path=/

``httponly`` and no ``secure``, on both the login page and the login POST, and
no ``X-Frame-Options`` on any response including ``/admin/``.

The deployment those cookies are issued by is TLS-only.
``ansible/templates/nginx-site.conf.j2`` serves ``listen 443 ssl`` with Let's
Encrypt certificates, and its port 80 server does nothing but
``return 301 https://{{ server.domain }}$request_uri``.

Impact
======

**The cookies.** A redirect from ``http://`` is not protection, because the
browser has already sent the request that gets redirected -- and it attaches
every cookie whose attributes allow it, which without ``Secure`` means all of
them. A typed address, an old bookmark, a link in an email, a QR code on a
label, an ``http://`` reference in the museum's other site: any of these puts
the logged-in gardener's ``sessionid`` on the wire in cleartext, once, before
the 301 arrives. Anybody on that path -- the café's wireless, the hotel's
router -- has a session cookie for a staff account. The CSRF cookie leaks the
same way, and although it is worth less on its own, an attacker holding both is
holding a working, forgeable pair.

This is the same destination as issue 049, by a different road: 049 is a
disclosed key that lets a session be *forged*, this is a live session
*handed over*. They do not depend on each other, which is the reason this is not
ordered behind it -- rotating the key does not close this window, and closing
this window does not make the key secret again.

**The framing.** With no ``X-Frame-Options`` header, any page on any site can
put this application in an invisible frame over its own controls. The admin is
the target that matters: a logged-in gardener made to click on what looks like
one page and is really the delete button of another. The label editor is the
second, because its Save rewrites every label from the request body (issue 010),
and because it is the page a gardener actually has open.

Severity is ``High`` for the cookies rather than for the framing. Clickjacking
needs a target who is both logged in and lured; the cleartext window needs
nothing but somebody typing an address they have typed a hundred times. The two
travel together here because they are one three-line change to one file, and
splitting them would be two issues about the same paragraph of settings.

What is embedded on purpose
===========================

This is the part that had to be checked rather than assumed, because the
straightforward fix breaks a live page.

``kasvimuseo/static/js/kasvimuseo/planted-species-iframe.js`` is a script the
museum's *other* site loads. It writes::

    <iframe src="//kasvit.ambitone.com/kasvimuseo/planted-species/" ...>

and then resizes that frame from a ``postMessage`` the framed page sends --
``static/js/kasvimuseo/iframe-height-fix.js``, which exists for no other
purpose. Two templates load it: ``reports/planted-species-list.html``
(``planted-species-list``) and ``reports/planted-species-base-compact.html``,
which is the base ``PlantedSpeciesCompact`` renders
(``planted-species-compact``).

That frame is cross-origin: the embedding page is on another host. So
``SAMEORIGIN`` would leave it blank, and ``DENY`` would too -- the choice
between those two does not enter into it. The two views are therefore exempted
one at a time, in ``kasvimuseo/urls.py``, with
``django.views.decorators.clickjacking.xframe_options_exempt`` -- the same shape
the staff-only decorators from issue 052 already take there.

Exempting them costs nothing worth having. Both are public, read-only reports:
no form that changes anything, no action that depends on who is logged in. There
is nothing on either page to trick anybody into clicking. Everything else --
the admin, the label editor, the observation pages, the API -- keeps the header.

``CSRF_COOKIE_HTTPONLY``: deliberately not set
==============================================

Two reasons, either of which is enough on its own.

**Django 1.5 has no such setting.** ``global_settings`` does not define it, and
``CsrfViewMiddleware.process_response`` in the installed 1.5.12 sets its cookie
with ``domain``, ``path``, ``max_age`` and ``secure`` and no ``httponly``
argument at all. Writing it into ``common_settings`` would be a setting Django
silently ignores, which is exactly the failure issue 019 is about, in a
different field. It arrives in Django 1.6, which the upgrade plan reaches at
**Stage 3** -- this said Stage 2, which is the photologue step; corrected when
Stage 3 ran. **That half of the argument is spent now.** 1.6 defines the
setting, defaulting to ``False``, so leaving it unset is a decision rather than
a non-event, and the reason below is the whole of it.

**And when it arrives it still must not be turned on blind.** The label editor's
Save reads the token out of ``document.cookie``::

    const match = document.cookie.match(/\bcsrftoken=(\w+)/);

(``kasvimuseo/templates/kasvimuseo/reports/planting-labels.html``). An HttpOnly
cookie is not in ``document.cookie``, so under
``CSRF_COOKIE_HTTPONLY = True`` that match fails and every gardener gets the
"this browser has no csrftoken cookie" alert issue 052 added -- a Save button
that cannot save, for everyone, for the same reason it used to fail for people
who had not been to the admin first.

The way out exists and is small: that page already renders ``{% csrf_token %}``
(issue 052 added it precisely so the cookie would be issued), so the JavaScript
could read the hidden input's ``value`` instead of the cookie and the setting
would then be free to take. That is a change to the label editor rather than to
the settings, the label editor is being worked on elsewhere, and this issue does
not need it: the setting does nothing in Django 1.5 either way. So it is left
unset, with the reason in the file, and
``test_csrf_cookie_httponly_is_not_a_setting_this_django_has`` fails on the day
the upgrade makes it a real question.

That day was upgrade plan Stage 3, and the test failed on that stage's first
suite run -- which is the only thing this issue asked of it. The answer is the
one written above: the setting stays unset until the label editor reads the
token from the ``{% csrf_token %}`` input rather than from ``document.cookie``.
The test is
``test_csrf_cookie_httponly_is_a_live_setting_now_and_stays_off`` now, asserting
the default Django supplies and that ``common_settings`` still overrides
nothing, and
``test_the_csrf_cookie_is_readable_by_the_label_editors_javascript`` beside it
asserts the behaviour the ruling rests on: the ``csrftoken`` cookie the label
editor's page issues carries no ``HttpOnly``.

Development must keep working over plain HTTP
=============================================

A ``Secure`` cookie is not kept or sent by a client that reached the page over
``http://`` -- with one exception that matters here: current browsers, and
curl, treat a *loopback* origin as trustworthy and keep it anyway. So the
breakage is real but uneven, and it was measured in both directions rather than
predicted.

**Reached by a name that is not loopback -- no login at all.** The same
development server, the same plain HTTP, addressed as ``http://devhost:8077/``
instead of ``http://127.0.0.1:8077/``::

    $ curl -c jar --resolve devhost:8077:127.0.0.1 \
          http://devhost:8077/accounts/login/
    $ grep csrftoken jar
    $                                # nothing: no cookie was kept

with the login POST then rejected for a missing CSRF token, and ``/admin/``
answering with the login form. This is not a hypothetical: issue 044 is about a
browser on *another machine* reaching this development server, which is how it
is used here, and ``ALLOWED_HOSTS = ['*']`` in the development settings exists
for the same reason.

**Reached on ``127.0.0.1`` -- almost everything works, which is worse.**
Chromium keeps the secure cookies from a loopback origin, so the browser suite
logs in and 28 of its 29 tests pass with the production value in place. The one
that does not is
``test_the_editor_and_its_endpoint_are_staff_only``: the request Playwright
makes through ``page.request``, outside the page, does not carry the secure
CSRF cookie, so the endpoint answers with a CSRF failure page instead of the
staff refusal the test asserts. A single failure of that shape, three files
away from any cookie, is exactly the kind of thing that costs an afternoon.

The suite's own client (``http://testserver``) does not enforce cookie
attributes at all, so it is indifferent -- but it is covered by the same
override, because a settings module that is right for two of the three ways it
is served and not the third is not right.

The values live in ``common_settings`` and are turned off in the two files that
already know they are not production: ``ylaneenkasvit/test_settings.py``, which
is built on ``common_settings`` for exactly this reason, and the ``modify()`` of
``ylaneenkasvit/local_settings.development.py``, which
``dev/kasvimuseo`` copies to the untracked ``local_settings.py``.

That direction matters. The secure value is the one a deployment inherits by
saying nothing, and relaxing it is an act, in a file named after the thing that
needs it. The other arrangement -- ``False`` in the common module and ``True``
in a production override -- would put the safe value in the file this repository
has the least control over: ``local_settings.py`` on the server is untracked, and
issue 051 is what that costs.

The fix
=======

``ylaneenkasvit/common_settings.py``::

    MIDDLEWARE_CLASSES = (
        ...
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

with the reasons in comments above each, and a comment where
``CSRF_COOKIE_HTTPONLY`` is not.

``ylaneenkasvit/test_settings.py`` and the ``modify()`` of
``ylaneenkasvit/local_settings.development.py`` set the two ``_SECURE`` flags
back to ``False``.

``kasvimuseo/urls.py`` wraps ``PlantedSpeciesList`` and
``PlantedSpeciesCompact`` in ``xframe_options_exempt``.

``SESSION_COOKIE_HTTPONLY`` needed nothing: Django 1.5 already defaults it to
``True``, and the measurement above shows the server issuing ``httponly``
today.

What it costs
=============

**Nothing is logged out.** Adding ``Secure`` to a cookie changes the attributes
of the next one issued; the sessions already in ``django_session`` are still
valid and their cookies are still sent, over the HTTPS the site serves. This is
unlike 057, which changed the stored format, and unlike 049, which changes the
key. It can ride the 049 window or go on any ordinary deploy.

**A gardener who has bookmarked ``http://`` sees no difference**, because nginx
still redirects and the browser then sends the cookie over TLS on the second
request. What changes is that the *first* request no longer carries it.

**No page loses its frame.** The two embedded reports are exempt and the browser
suite exercises the rest.

**It takes effect on the next deploy**, which is the repository-half /
server-half split issues 025, 049 and 051 describe. Nothing here can change what
the running uWSGI has already loaded.

What this does not cover
========================

``nginx-site.conf.j2`` sends no ``Strict-Transport-Security`` header, so a
browser that has never been told otherwise still makes that first ``http://``
request -- this issue removes what it leaks, HSTS would stop it being made.
That is the server-side complement, it is a different file and a different half
of the deployment, and it is **issue 060**, filed separately and open.

Verification
============

* ``dev/kasvimuseo app test`` -- 449 tests pass. With the four changed source
  files reverted and the tests kept, twelve of the sixteen new and changed tests
  fail: both settings assertions on ``AttributeError``, the secure-cookie and
  secure-CSRF-cookie behaviour tests, the development-override test, the
  middleware and ``X_FRAME_OPTIONS`` assertions, all three
  ``refuses_to_be_framed`` behaviour tests, and both of issue 019's middleware
  tests.
* The four that pass either way are named here rather than counted as evidence.
  ``test_the_suite_serves_plain_http`` passes because Django's default is
  ``False`` too -- it guards the override, not the fix. The two
  ``test_the_embedded_reports_are_exempt`` cases pass vacuously without the
  middleware, since without it no response has the header; what gives them force
  is the three tests beside them that require it everywhere else.
  ``test_csrf_cookie_httponly_is_not_a_setting_this_django_has`` pins the
  decision not to set it, and is written to fail when the upgrade makes that a
  live question.
* ``dev/kasvimuseo app browser-test`` -- 29 passed. Run once more with
  ``test_settings``' two override lines removed, to find out whether that
  override is load-bearing or a precaution: 1 failed, 28 passed, and the
  failure is the one described above. It is load-bearing, and now it is
  documented in the file that carries it.
* Through the running server, after the change, over ``dev/kasvimuseo app
  run``. With the development override in place: the login sticks, the admin
  answers 200 with the dashboard, ``X-Frame-Options: SAMEORIGIN`` is on it, and
  ``/kasvimuseo/planted-species/`` carries no such header -- the exemption,
  end to end. With the override removed, so that the server runs the values
  production will::

      Set-Cookie: csrftoken=VUii...; Max-Age=31449600; Path=/; secure
      Set-Cookie: sessionid=agte...; httponly; Max-Age=1209600; Path=/; secure

  which is the header this issue was filed about, now carrying both
  attributes.
