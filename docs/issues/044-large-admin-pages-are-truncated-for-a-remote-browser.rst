=================================================================
Issue 044: Large admin pages are truncated for a remote browser
=================================================================

:Status: In progress
:Severity: High
:Area: dev environment / serving
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: (none -- the suite uses the test client, which never crosses a socket)
:Depends on: (none)
:Blocks: (none)
:Related: 040 -- the same three buttons, one Finnish and two English
    013 -- another admin declaration that claims something untrue
    045 -- the other report that needed a browser to settle
    010 -- the labels API, whose POST deletes every label before recreating
    it, which is what makes a truncated load worth checking on that page
:Decision: Option 1, taken 2026-07-30: the development site is served by
    gunicorn, and ``manage.py runserver`` stays available behind
    ``dev/kasvimuseo app run --runserver``. Taken without waiting for the
    measurements, because it is right whatever they say -- see "Decision"
    below, which also records what it does not settle.
:Resolution: ``1bced8d`` "dev: serve the development site with gunicorn" fixes
    the development environment and makes the failure audible. It does not stop
    it: measured from the laptop on 2026-07-30, the labels URL is still cut, at
    42,974 bytes of 54,613, and now says so (``curl`` exit 18). The cause is
    below HTTP -- pasta or the tailnet. See "What the laptop said" and "What
    the maintainer must still confirm".

Problem
=======

Reported as missing save buttons: on ``species``, ``plot`` and ``planting``
change forms the whole submit row -- ``Tallenna``, ``Save and add another``,
``Save and continue editing`` -- does not appear, in Firefox 152 on Linux,
against the development server. The other nine registered models are fine, and
production is fine.

The buttons are not the problem. **The page stops arriving before it gets to
them.** The DOM of ``/admin/kasvimuseo/species/6/``, copied from the browser
that shows it, ends like this::

    <div class="grp-row grp-cells-1 notes ">
      <div class="l-2c-fluid l-d-4">
        <div class="c-1"><label for="id_observation_set-__prefix__-notes">Muistiinpanoja</label></div>
        <div class="c-2"></div>
      </div>
    </div></fieldset></div></div></div></div></form></div></article></div>

The ``notes`` row has no ``<textarea>``, the ``environment`` row that follows it
in the template is absent, and then every open element closes at once. That
cascade is the HTML parser reaching end of stream, not markup the server wrote.
Everything after that point -- the rest of the inline, the closing of the form,
and the submit row -- never arrived.

The setup it happens in
=======================

=================== ==========================================================
 Client              Firefox 152.0.5, Linux, on an Atom laptop -- a different
                     machine from the server
 URL                 ``http://gogo.crane-boa.ts.net:8000/admin/kasvimuseo/species/6/``
 Path                Tailscale (host ``gogo``, ``100.81.121.7``) to a port
                     published by rootless podman with pasta,
                     ``0.0.0.0:8000 -> 8000``
 Server              ``python ylaneenkasvit/manage.py runserver 0.0.0.0:8000``
                     in the dev container -- Django 1.5.1, ``wsgiref``,
                     single-threaded
 Checkout            ``/home/agent/prg/kasvimuseo`` on ``master``,
                     bind-mounted at ``/src``
 Settings            ``ylaneenkasvit/local_settings.py``, byte-identical to
                     ``local_settings.development.py``: ``DEBUG`` on,
                     ``STATIC_URL`` ``/static/``, ``ALLOWED_HOSTS`` ``['*']``
 Data                The February 2025 production dump
 Production          uwsgi behind a web server. Unaffected. (Not gunicorn --
                     see "What it is not".)
=================== ==========================================================

Note for whoever picks this up: at the time of writing, that container has been
removed and the cluster under ``.dev/pgdata`` is stopped, so the first step is
``dev/kasvimuseo app run`` again. The measurements below were taken against a
second copy of the same dump in a task worktree, on port 9633.

Where the stream stops
======================

Requested over the loopback interface on the server host, the same page for the
same object is **52,119 bytes, complete, three times out of three**, with the
footer present. The two markers surrounding the reporter's cut sit at bytes
42,435 (``id_observation_set-__prefix__-notes``) and 42,786
(``...-environment``), so roughly 42 KB of 52 KB arrived and about 10 KB were
lost.

An earlier version of this paragraph ended "the browser had a
``Content-Length`` promising the rest". **It did not** -- ``runserver`` sends
none, and that turns out to be half of why this issue was so hard to see. See
"Nothing was in a position to notice" below.

That single number explains the model list, which never made sense as a model
list. Measured against the same database:

============================ ========= =========================
 Page                         Bytes     Reported
============================ ========= =========================
 ``species/97``                135,831  broken
 ``planting/22``                92,652  broken
 ``planting/1``                 70,584  broken
 ``plot/1``                     60,065  broken
 ``species/6``                  52,119  broken
 ``plot/2``                     43,942  broken
 ``observation/1``              27,548  works
 ``auth/user/1``                27,010  works
 ``care/1``                     26,261  works
 ``auth/group/1``               22,105  works
 ``contact/1``                  17,354  works
 ``bed/2``                      15,518  works
 ``photologue/photo/1``          1,672  works
============================ ========= =========================

Everything reported broken is larger than 43 KB; everything reported working is
smaller than 28 KB. The boundary falls exactly where the reporter's page was
cut. (**As a rule this did not survive** -- a 360 KB page has since been seen
to arrive whole. The table is still the measurement it was; it is the sentence
above that was too strong. See "The ``location`` contradiction".) Those three admin classes declare inlines, which is why their forms are the
big ones -- the inline set is the size, not the cause.

**One page contradicts this and needed checking first:** ``location`` is by far
the largest form in the application -- ``location/2`` is 360 KB and
``location/8`` is 544 KB, because every observation inline repeats a 60-option
select -- and it is reported as working. That check was done, as far as it can
be done from the server; the next section is its answer.

The ``location`` contradiction
==============================

**Settled from the laptop on 2026-07-30, and it goes against the size
explanation.** ``/admin/kasvimuseo/location/2/`` -- 360,391 bytes, seven times
the page that started this issue -- loads over the tailnet with its related
objects appearing gradually and **the footer with the save buttons at the end
of it**. The whole response arrives. Read what follows knowing that: the
paragraphs below were written to say what the answer would mean, and the answer
is the one that reopens the question. See "What the laptop said" for the rest
of that round and for what is now suspected.

One caveat on the caveat: that page was opened after the change below, so what
it proves outright is that a 360 KB response *can* cross this path today. It
does not distinguish "``location`` always worked, and the size rule was never
right" from "gunicorn fixed the admin pages, ``location`` among them". The one
page that separates those two is ``species/6``, which is in the next round.

What the server says, measured 2026-07-30 against the same dump:

* Both ``location`` change forms render **complete** over loopback:
  ``location/2`` is 360,391 bytes and ``location/8`` is 544,765, ending in
  ``</body></html>``, under gunicorn and under ``runserver`` alike.
* The submit row is **680 bytes from the end of every change form there is**.
  ``name="_save"`` occurs at byte 24,553 of 25,233 on ``photologue/gallery/1``,
  26,929 of 27,609 on ``observation/1``, 43,321 of 44,001 on ``plot/2``, 51,550
  of 52,230 on ``species/6``, 92,041 of 92,721 on ``planting/22``, and 359,711
  of 360,391 on ``location/2``. Grappelli's ``change_form.html`` puts it in
  ``submit_buttons_bottom``, so its distance from the end is a constant and its
  distance from the *start* is the size of the page.

So there is no way for ``location`` to be both cut in the 42.8 KB band and to
show its buttons: a cut that removes the submit row from a 52 KB page removes it
from a 360 KB one *a fortiori*. The size explanation and a working ``location``
cannot both be true, and only the affected machine can say which it is.

Two things make "never opened" the likely reading, neither of them proof:

* **The arithmetic matches the admin index rather than a checklist.** The index
  lists exactly twelve models -- ``bed``, ``care``, ``contact``, ``location``,
  ``observation``, ``planting``, ``plot``, ``species``, ``auth/user``,
  ``auth/group``, ``photologue/gallery`` and ``photologue/photo``. Three were
  reported broken and the report says "the other nine": twelve minus three.
  Of those nine, seven appear in the size table above, all measured under
  28 KB. The two that do not are ``photologue/gallery`` -- one row in this
  database, 25 KB, well under the boundary -- and ``location``.
* ``location``'s own changelist is 65,078 bytes, over the boundary itself, so
  on the affected machine that list arrives cut too. Its first rows and their
  links survive a cut at 42.8 KB, so this does not prevent opening a
  ``location``; it does mean every page in that corner of the admin looks
  subtly wrong, which is not an invitation to go there.

**If a ``location`` change form does show its submit row on the laptop, stop
reading here**: the size explanation is wrong, the boundary in the table above
is a coincidence of which pages happened to be opened, and this issue reopens on
a different track. Nothing in the fix below depends on the answer -- a
development server that cannot report a short response is worth replacing either
way -- but the diagnosis does.

A second URL, with no admin and no login, is cut in the same band
=================================================================

Reported 2026-07-30, from the browser, against the same host::

    http://gogo.crane-boa.ts.net:8000/kasvimuseo/planting-labels/data/
    SyntaxError: JSON.parse: unterminated string at line 1 column 42872 of the JSON data

The body the browser got ends mid-string::

    , {"nicknames": [""], "all_photos": {"134": "/media/photologue/photos/cache/S%C3%A4rkynytsyd%C3%A4n.

That is the same failure as above, one layer down. The page is
``/kasvimuseo/planting-labels/``, whose Vue editor fetches its data from
``PlantedSpeciesLabelsApi`` at the URL shown; the response stops part way
through and the parser reports the first token it cannot finish. A truncated
HTML page closes its own tags, so it merely looks wrong -- truncated JSON has
no such tolerance, which is why this one announces itself.

Requested on ``gogo`` itself, that URL answers ``200``,
``content-type: application/json``, **54,613 bytes, four times out of four**,
parsing cleanly and ending ``..."genus": "Ribes"}]}``; the same with
``--compressed`` and with a Firefox ``User-Agent``. The body is pure ASCII
(54,613 characters in 54,613 bytes), so no encoding is implicated -- the
``%C3%A4`` in the fragment above is already percent-encoded in the payload.
That measurement carries the same caveat as the loopback figures above: it
never left the machine, so it says nothing about the path from the laptop.

The quoted fragment locates the cut exactly. It occurs once in the complete
body, at zero-based offset 42,771, and is 100 bytes long, so **the browser received
42,871 bytes of 54,613 and lost 11,742.** Against ``species/6``, whose cut was
bracketed between markers at 42,435 and 42,786 bytes:

=========================== ================ ================ ==============
 Response                    Complete         Received         Lost
=========================== ================ ================ ==============
 ``admin/.../species/6/``    52,119 bytes     42,435..42,786   ~10 KB
 ``planting-labels/data/``   54,613 bytes     42,871 (exact)   11,742
=========================== ================ ================ ==============

Two different views, two different content types, two different total sizes,
and the two cuts land within 440 bytes of each other -- less if the admin cut
was nearer the upper marker, as little as 85 -- which is one part in a hundred
of either response. By the test set out under "How to confirm" below, **that is a
constant byte count, which points at a buffer rather than at the network**: an
MTU or path problem would not stop at the same offset in two responses that
have nothing else in common. Suspects 1 and 2 (``wsgiref`` and the pasta port
publication) move ahead of suspect 3. It is two data points rather than a
series, so it is not proof; the ``curl`` loop below is still what settles it,
and a third cut in the same band would close the question.

Three other things follow from this URL:

* **The save hazard has to be checked here too**, because this page's POST
  replaces every label rather than one form's fields. It turns out not to be
  reachable; see "The label editor cannot save from a failed load" below.
* **The title of this issue is now too narrow.** Nothing about the admin,
  Grappelli, inlines, change forms or ``save_on_top`` is involved here. The
  size table above still holds, but as a property of responses, not of admin
  pages. The file is not renamed, because :doc:`index` refers to it by name.
* **The confirmation gets much easier.** This URL is public: it needs no
  session, so the CSRF login dance below is not required to measure it.

What it is not
==============

* **Not the application.** The response is complete and correct over loopback,
  and complete when fetched over this host's own tailnet address (which never
  leaves the machine). Nothing between the February 2025 production release and
  ``b801d8e`` touches the change form.
* **Not the browser.** A partial DOM with a parser-closed tail is what a browser
  does with a short response; it is not something CSS, an extension or a zoom
  level can produce. Earlier work on this issue chased all three and found
  nothing, correctly.
* **Not the data or the installation.** Same restored production dump, same
  container image, same bind-mounted checkout, and an
  ``ylaneenkasvit/local_settings.py`` byte-identical to the template.
* **Not production**, which serves through a real WSGI server behind a real web
  server rather than through ``manage.py runserver``. (That server is uwsgi,
  not gunicorn: ``ansible/roles/akaihola.uwsgi``, ``uwsgi.ini`` and a systemd
  unit. gunicorn is pinned in ``requirements/production.txt`` and installed
  everywhere, but nothing in the deployment starts it. The table at the top of
  this file said "gunicorn behind a web server"; it is corrected here rather
  than silently, because it is what option 1 below was argued from.)

The remaining difference is the path between the two. The reporter reaches the
site at ``http://gogo.crane-boa.ts.net:8000/`` -- from a laptop, over Tailscale,
to a Django 1.5 ``runserver`` inside a rootless podman container published with
pasta. Every one of those is a plausible place to lose the tail of a 52 KB
response, and none of them can be exercised from the server host itself, which
is why this reproduces for the reporter and for nobody else:

1. **``manage.py runserver``** is ``wsgiref``: single-threaded, and explicitly
   documented as not for anything but local development. Django 1.5's is the
   oldest version of it in this project's history.
2. **The pasta port publication**, which is the layer that differs between a
   loopback request and one arriving on the host's external interface.
3. **Tailscale's 1280-byte MTU**, if path MTU discovery is failing somewhere: a
   large response stalls or resets partway while a small one completes.

Nothing was in a position to notice
===================================

Measured 2026-07-30, on ``gogo``, against ``runserver``::

    HTTP/1.0 200 OK
    Server: WSGIServer/0.1 Python/2.7.18
    Content-Type: application/json

That is the whole header block: **HTTP/1.0, no ``Content-Length``, no
``Transfer-Encoding``**. Django 1.5 sets a length on static-file responses and
on nothing else, and ``wsgiref`` adds none, so for every page in the table
above the length of the body is defined by the connection closing. A response
that stops early is therefore *byte-for-byte indistinguishable* from a complete
one, at every layer: the browser has nothing to compare against and renders
what it has, and ``curl`` exits 0 and reports a ``size_download`` that looks
like the right answer for a page nobody has measured before.

That is why this arrived as "the save buttons are missing" rather than as a
transfer error, and it is also why the ``Content-Length`` comparison this file
originally prescribed cannot work.

The same request, through gunicorn::

    HTTP/1.1 200 OK
    Server: gunicorn/0.17.4
    Transfer-Encoding: chunked

Chunked framing carries its own end marker, so a short read is an error rather
than an answer. Demonstrated with a 30-line proxy that forwards one request and
then drops the connection at 42,871 bytes -- the exact count the reporter's
browser received -- in front of each server in turn, both serving the same
labels URL from the same database:

=============== ================== ==============================================
 Server          ``curl`` exit      What the client is told
=============== ================== ==============================================
 ``runserver``   0                  a complete 42,745-byte response
 gunicorn        18                 ``transfer closed with outstanding read
                                    data remaining``
=============== ================== ==============================================

This does not make the bytes arrive. If something on the path is dropping the
tail of a large response it will go on dropping it, and the browser will show a
failed page instead of a half-rendered one. What it does is end the silence:
after this change, a truncation on the laptop is a visible network error, in
the browser's console and in any ``curl`` run against the site, and the labels
editor's ``.catch`` finally fires -- see the next section, which is why it does
not fire today.

Do not save one of these forms
==============================

While this is open, a truncated change form must not be submitted. The fields
after the cut are absent from the POST, and Django reads an absent field as an
empty value, so saving would blank whatever did not arrive. On ``species/6``
the cut lands inside the spare empty inline and would probably be harmless; on
``species/97`` at 136 KB it lands in the middle of real observation data. This
is also why "put a save button at the top of the form so it survives the
truncation" is the wrong fix: it would make a data-losing save easy to perform.

The label editor cannot save from a failed load
===============================================

The page from the second observation would carry the same risk in a sharper
form, and it is worth checking that it does not. ``PlantedSpeciesLabelsApi.post``
does ``Label.objects.all().delete()`` and then recreates a label from every item
in the submitted list, so what is posted is the whole of the new state: a
species missing from a partial load would have its label deleted rather than
left alone, and the plantings that pointed at it re-linked or dropped (issue 010
is the other hazard on that same POST).

Read as written, the page is safe today, and it is worth saying exactly why,
because the margin is thin. In
``kasvimuseo/templates/kasvimuseo/reports/planting-labels.html``:

* ``object_list`` starts as ``[]``, and the ``axios.get`` that fills it has a
  ``.catch`` that does nothing but ``alert('error')``. A body that will not
  parse therefore leaves the list empty -- which is also the symptom to expect
  on the affected machine: an alert reading ``error`` and no labels.
* The ``Save changes`` button is bound to ``disableSave``, which starts
  ``true`` and is cleared only by the ``enable-save`` event. That event has one
  origin, a ``watch`` on ``species.visible`` inside the per-label component,
  and an empty list renders none of those components. So nothing can enable the
  button and nothing can be posted.

The hazard is latent rather than live: it needs the editor to hold *some* of
the labels, and ``JSON.parse`` is all or nothing. But it is one edit away --
anything that recovers partial data, or enables the button on another event,
turns a truncated load into a silent deletion of every label that did not
arrive. Keep the delete-and-recreate in mind if the fetch is ever made more
forgiving.

Confirmed in a browser, 2026-07-30
----------------------------------

Not taken on trust. Chromium via Playwright against the development site, with
the response to ``/kasvimuseo/planting-labels/data/`` cut to 42,871 bytes --
the reporter's byte count -- and a complete load beside it as a control:

======================================= ============ ============ ==============
 Load                                    Labels       Checkboxes   ``Save changes``
======================================= ============ ============ ==============
 complete (54,613 bytes)                 149          149          disabled
 complete, after one checkbox clicked    149          149          **enabled**
 cut at 42,871 bytes                     0            0            disabled
 cut, after clicking (nothing to click)  0            0            disabled
======================================= ============ ============ ==============

The middle row is the control: the check is sensitive enough to see the button
become clickable, and on the truncated load there is nothing that makes it so.
So the page is safe as the section above argues -- **with one correction**. The
predicted ``alert('error')`` does not appear. The current axios (1.19.0, loaded
unpinned from ``unpkg.com``) parses a JSON body with ``silentJSONParsing``, so
an unterminated body is not an error but a plain string; ``response.data`` is
then a string, ``response.data.object_list`` is ``undefined``, the assignment
succeeds, and the ``.catch`` never runs. The user gets an empty label sheet and
no message at all.

That is worse than an alert, and it is the same silence as everywhere else in
this issue: nothing anywhere is told that bytes went missing. It is also
version-dependent -- the unpinned CDN URL means another machine can load an
axios that does throw, which is presumably what put the ``SyntaxError`` in the
reporter's console. Under gunicorn the truncation becomes a transport error
instead of a parse one, and *that* does reach the ``.catch``.

How to confirm, from the laptop
===============================

All of this is run against a site started with ``dev/kasvimuseo app run``,
which is now gunicorn. **The ``Content-Length`` comparison first written here
does not work** and never did: neither server sends one for a rendered page
(see "Nothing was in a position to notice"). What replaces it is better --
under gunicorn a short response makes ``curl`` exit non-zero, so the test is
the exit status, and ``curl`` prints where it stopped by way of
``size_download``.

**Open a ``location`` change form first.** One page, before any measuring:

    ``http://gogo.crane-boa.ts.net:8000/admin/kasvimuseo/location/2/``

and scroll to the bottom. If ``Tallenna`` is there, the size explanation in this
file is wrong -- say so and stop; nothing further down is worth measuring until
that is re-thought. If it is missing, as ``species/6`` is, the boundary holds and
everything below applies.

**Then the one that needs no login.** The labels data URL from the second
observation is public, so a single command decides the question::

    curl -sS -o body.json -w 'exit=%{exitcode} downloaded=%{size_download}\n' \
         http://gogo.crane-boa.ts.net:8000/kasvimuseo/planting-labels/data/

Complete is ``exit=0 downloaded=54613``. Anything else is the failure, and
``curl`` names it: ``(18) transfer closed with outstanding read data
remaining``. Repeat it a few times and note **where** it stops each time: the
same offset twice more makes the buffer reading above hard to argue with, a
different one each time sends this back to the network.

The admin measurement is the fuller one, since it varies the response size.
It needs a logged-in session, and the login is a CSRF-protected
POST, so it is two steps. This is the exact sequence used for the loopback
figures above; run it on the machine that shows the problem, against the
tailnet name::

    HOST=http://gogo.crane-boa.ts.net:8000
    TOK=$(curl -s -c c.txt $HOST/admin/ \
          | grep -o "name='csrfmiddlewaretoken' value='[^']*'" \
          | head -1 | sed "s/.*value='//;s/'//")
    curl -s -b c.txt -c c.txt -o /dev/null -e $HOST/admin/ \
         -d "csrfmiddlewaretoken=$TOK&username=<user>&password=<pass>&this_is_the_login_form=1&next=/admin/" \
         $HOST/admin/

    for p in observation/1 species/6 plot/2 planting/22 location/2; do
        curl -sS -b c.txt "$HOST/admin/kasvimuseo/$p/" -o body.html \
             -w "$p exit=%{exitcode} downloaded=%{size_download}\n"
    done

The complete sizes over loopback, for comparison: ``observation/1`` 27,609,
``species/6`` 52,230, ``plot/2`` 44,001, ``planting/22`` 92,721, ``location/2``
360,391.

**A non-zero exit, or a ``size_download`` short of those, means the response is
being cut before Firefox ever sees it**, and the browser is exonerated for
good. The page just under the boundary (``observation/1``, 27 KB) should come
through whole; where exactly the cut falls on the larger ones is the strongest
clue to which of the three layers is responsible -- a constant byte count
points at a buffer, a varying one at the network.

Then the same loop through an SSH tunnel, which turns the remote request into a
loopback one on the server side::

    ssh -N -L 8000:127.0.0.1:8000 gogo    # then use HOST=http://127.0.0.1:8000

Whole through the tunnel and cut without it finishes the application as a
suspect and makes this a dev-environment issue only.

For comparison, the loopback baseline on the server host, taken the same way
against the same dump, was 52,119 bytes for ``species/6`` on all three of three
attempts, with ``grp-fixed-footer`` present. Requests to the host's own tailnet
address (``100.81.121.7``) were also complete -- but that traffic never leaves
the machine, so it says nothing about the path from the laptop.

What the laptop said, 2026-07-30
================================

The first round, run by the maintainer against the site as it now runs -- the
``exit=18`` below is gunicorn's chunked framing, so this is the new server.

1. **``location/2`` renders whole**, footer and save buttons present, as above.
2. **The labels URL is still cut**, and now says so::

       curl: (18) transfer closed with outstanding read data remaining
       exit=18 downloaded=42974

   Complete is 54,613. So the bytes still go missing; what changed is that
   nothing pretends otherwise any more. This is the change doing exactly the
   job it was taken for, and no more.
3. **The admin loop measured nothing.** Every line came back at about 7,130
   bytes -- ``observation/1`` 7,138, ``species/6`` 7,130, ``plot/2`` 7,124,
   ``planting/22`` 7,134, ``location/2`` 7,132 -- which is the admin **login
   page**, not a change form. The ``<user>`` and ``<pass>`` placeholders were
   posted literally, so the session was never established and every request
   redirected. The sizes differ only by the length of the ``next=`` parameter
   in each form.
4. **The tunnel run measured the same nothing**, for the same reason: identical
   byte counts, so it too fetched five login pages. The tunnel comparison is
   still owed.

Where that leaves the diagnosis
-------------------------------

**The size rule, as this file stated it, is refuted.** "Everything larger than
43 KB is cut" cannot survive a 360 KB page arriving whole. What is left is
narrower and stranger: a 54,613-byte response is cut at 42,974 bytes, and was
cut at 42,871 by a different client against a different server, while a
360,391-byte one is not cut at all.

Those two cut points are 103 bytes apart, which is what makes this hard to file
under either heading offered above. A buffer would be expected to cut at the
same offset twice; the network reading predicts no particular offset at all.
Something that stalls after roughly 42--43 KB *in flight* -- a window that
stops being refilled rather than a boundary in the data -- fits both numbers,
and fits a large page surviving whenever the client happens to drain fast
enough. That is a hypothesis, not a finding: it rests on two samples, and the
next round is designed to get more.

It also means **suspect 1 is closer to being cleared than the numbers above
suggested**. ``wsgiref`` is gone from the path and the cut is not: whatever
does this lives below the WSGI server, in pasta or in the tailnet. Suspect 3
(the MTU) is no longer the outsider it was ranked as, and there is a cheap test
for it in the next round.

Options
=======

1. **Serve the development site with gunicorn** rather than ``runserver``.
   It is already a dependency (see issue 021, which wants it removed as an
   installed *app* -- that is a different thing), it is the kind of server
   production uses, so the dev environment stops differing from production in
   the one way that matters here, and ``dev/kasvimuseo app run`` is the only
   place to change. ``runserver`` stays available for a loopback-only session.
   **This is the one taken; see "Decision" below.**
2. **Reach the dev server over an SSH tunnel** and keep ``runserver``. No code
   changes; it is a line in the README and a habit. It also removes the
   ``ALLOWED_HOSTS = ['*']`` in ``local_settings.development.py``, which exists
   only because the server is published under an arbitrary name (issue 026).
3. **Chase the MTU** if the ``curl`` measurements point at the network rather
   than the server. ``tailscale ping --verbose`` reports the negotiated path;
   an MTU mismatch is a property of the tailnet, not of this repository.
   **This is where the first round of measurements points**, since the cut
   survived the change of WSGI server. Commands under "What the maintainer must
   still confirm", step 5.

Decision
========

**Option 1, on 2026-07-30.** ``dev/kasvimuseo app run`` starts

::

    gunicorn ylaneenkasvit.wsgi:application --bind 0.0.0.0:8000 \
        --workers 1 --timeout 300 --access-logfile - --error-logfile -

and ``dev/kasvimuseo app run --runserver`` still starts the old one. Two
supporting changes came with it:

* ``ylaneenkasvit/urls.py`` wires ``staticfiles_urlpatterns()`` in.
  ``runserver`` serves ``STATIC_URL`` from the finders by itself and no other
  server does, so without this the admin comes up unstyled. It is
  ``DEBUG``-gated by ``django.conf.urls.static.static``, so production is
  untouched.
* ``README.rst`` says which server runs when, and what is given up: gunicorn
  0.17.4 has no ``--reload``, so editing Python needs a restart or
  ``podman kill --signal HUP``. Templates and static files are still re-read
  per request.

Taken before the measurements rather than after, because it does not depend on
them. Whichever of the three layers is cutting the response, a development
server that cannot state the length of what it is sending has no way to report
the cut, and that -- not the missing buttons -- is what made this issue expensive
to find. Options 2 and 3 both leave that in place.

What it does **not** claim:

* **It does not prove the cause.** If ``wsgiref`` was the thing dropping the
  tail, this fixes the report outright; if pasta or the tailnet MTU is, the
  bytes still go missing and the change converts a silently half-rendered page
  into a visible error. Both are improvements and only the laptop can say which
  one happened. *It said the second one*: the labels URL is still cut under
  gunicorn, loudly. See "What the laptop said".
* **It does not settle the ``location`` contradiction.** That was settled from
  the laptop instead, against the size explanation.
* **It changes nothing in production**, which does not run ``runserver`` and
  does not serve ``/static/`` from Django.

Verified on ``gogo``, 2026-07-30, restored February 2025 dump, over loopback,
under gunicorn: ``species/6`` 52,230 bytes, ``species/97`` 135,997,
``plot/2`` 44,001, ``planting/22`` 92,721, ``location/2`` 360,391,
``location/8`` 544,765, ``observation/1`` 27,609 -- every one ending in
``</body></html>`` with its submit row present, and byte-for-byte the same
counts as under ``runserver``. ``/kasvimuseo/planting-labels/data/`` is 54,613
bytes and parses. Static files carry a ``Content-Length`` and match it exactly
(``grappelli/stylesheets/screen.css`` 167,158, ``css/kasvimuseo.admin.css``
2,341); ``/media/`` still redirects to the fallback host. ``dev/kasvimuseo app
test``: 357 passed.

What the maintainer must still confirm
======================================

This is why ``Status`` is not ``Fixed``: the labels URL is still cut, and the
first round left three questions open. All of the following runs from the
laptop, and **none of it needs a login** -- that is deliberate, after round
one.

**1. Is the cut at a fixed offset?** Ten fetches of the public URL, printing
where each one stopped::

    for i in $(seq 10); do
        curl -s -o /dev/null -w "exit=%{exitcode} downloaded=%{size_download}\n" \
             http://gogo.crane-boa.ts.net:8000/kasvimuseo/planting-labels/data/
    done

Complete is 54,613. Ten identical short counts is a buffer and names its size;
ten different ones is the network; a mixture of whole and cut is the stall
this file now suspects, and the proportion is itself a measurement.

**2. Does the same URL survive the tunnel?** The comparison round one owed::

    ssh -N -L 8000:127.0.0.1:8000 gogo &
    for i in $(seq 10); do
        curl -s -o /dev/null -w "exit=%{exitcode} downloaded=%{size_download}\n" \
             http://127.0.0.1:8000/kasvimuseo/planting-labels/data/
    done

Whole through the tunnel and cut without it puts this below HTTP for good, in
pasta or the tailnet, and finishes both the application and the WSGI server as
suspects.

**3. Is it size, or is it this response?** Five public static files, each with
a real ``Content-Length`` to check against, two of them larger than the JSON
that fails::

    B=http://gogo.crane-boa.ts.net:8000/static
    for u in css/kasvimuseo.admin.css:2341 \
             admin/js/core.js:6662 \
             grappelli/js/grappelli.min.js:27925 \
             grappelli/jquery/jquery-1.7.2.min.js:94840 \
             grappelli/stylesheets/screen.css:167158; do
        curl -s -o /dev/null -w "${u#*:} expected, %{size_download} got, exit=%{exitcode}\n" \
             "$B/${u%%:*}"
    done

If 94,840 and 167,158 arrive whole while 54,613 does not, size is not the rule
and the difference is in how the response is written -- Django serves a static
file through a file wrapper in many small writes, and a rendered page as one
string.

**4. Is the reported symptom actually gone?** Open
``/admin/kasvimuseo/species/6/`` in Firefox -- the exact page this issue was
filed about -- and look for ``Tallenna``. This is the one that says whether the
change fixed the report or only made its failures audible, and it is the
difference between ``Fixed`` and ``In progress``.

**5. If 2 says the tailnet**, the MTU test is two commands::

    tailscale ping --verbose gogo
    ping -M do -s 1252 100.81.121.7      # 1280-byte packets, no fragmentation
    ping -M do -s 1372 100.81.121.7      # 1400 -- should fail on a 1280 path

A 1400-byte probe that neither succeeds nor reports "message too long" is a
path-MTU black hole, which is option 3, and it is a property of the tailnet
rather than of this repository.

Independently of all of this
============================

``SpeciesAdmin``, ``PlotAdmin``, ``PlantingAdmin`` and five other admin classes
set ``save_on_top = True``, and it has never done anything: Grappelli's
``change_form.html`` renders ``{% submit_row %}`` once, in
``{% block submit_buttons_bottom %}``, with no top block at all. That is worth
either honouring with a small template override or deleting, so the setting
stops claiming something untrue -- but **after** this issue is fixed, for the
data-loss reason above.

See also
========

Issue 013 (stale ``FIXME`` comments claiming admin features are broken -- the
same admin module, the same kind of untrue declaration), issue 040 (half the
admin chrome is English -- which is why one button says ``Tallenna`` and the two
beside it do not), issue 045 (the other report that needed a browser to settle),
issue 021 (gunicorn, which option 1 has now given a real use -- it is installed
as an *app* for no reason, which is a separate thing from being run as a
server).
