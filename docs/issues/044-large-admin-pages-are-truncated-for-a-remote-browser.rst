=================================================================
Issue 044: Large admin pages are truncated for a remote browser
=================================================================

:Status: Accepted
:Claimed: its own task, since 2026-07-29 (see ``incoming.rst``)
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
:Decision: Accepted for work on 2026-07-29 and taken up as its own task; which
    of the three options below is taken is still open, and depends on what the
    measurements from the affected machine say.
:Resolution: (none yet)

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
 Production          gunicorn behind a web server. Unaffected.
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
lost. The browser had a ``Content-Length`` promising the rest.

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
cut. Those three admin classes declare inlines, which is why their forms are the
big ones -- the inline set is the size, not the cause.

**One page contradicts this and needs checking first:** ``location`` is by far
the largest form in the application -- ``location/2`` is 360 KB and
``location/8`` is 544 KB, because every observation inline repeats a 60-option
select -- and it is reported as working. It may simply not have been opened; the
report says "the other nine models", which is a count rather than a checklist.
But if a ``location`` change form really does render its submit row on the
affected machine, the size explanation is wrong and everything below it needs
reopening on a different track. It is one page to open, and it should be the
first thing the follow-up does.

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
* **Not production**, which serves through gunicorn behind a real web server
  rather than through ``manage.py runserver``.

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
arrive. Confirm the empty-and-disabled behaviour in the browser before touching
this page, and keep the delete-and-recreate in mind if the fetch is ever made
more forgiving.

How to confirm, from the laptop
===============================

**Start with the one that needs no login.** The labels data URL from the second
observation is public, so a single command decides the question::

    curl -s -D h.txt -o body.json -w 'downloaded=%{size_download}\n' \
         http://gogo.crane-boa.ts.net:8000/kasvimuseo/planting-labels/data/
    grep -i '^content-length' h.txt      # and compare; complete is 54,613 bytes

Short from the laptop and whole from ``gogo`` is the whole of this issue in two
commands. Repeat it a few times and note **where** it stops each time: the same
offset twice more makes the buffer reading above hard to argue with, a
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
        curl -s -D h.txt -b c.txt "$HOST/admin/kasvimuseo/$p/" -o body.html \
             -w "$p downloaded=%{size_download} "
        grep -i '^content-length' h.txt
    done

**If ``size_download`` is smaller than ``Content-Length``, the response is being
cut before Firefox ever sees it**, and the browser is exonerated for good. The
page just under the boundary (``observation/1``, 27 KB) should come through
whole; where exactly the cut falls on the larger ones is the strongest clue to
which of the three layers is responsible -- a constant byte count points at a
buffer, a varying one at the network.

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

Options
=======

1. **Serve the development site with gunicorn** rather than ``runserver``.
   It is already a dependency (see issue 021, which wants it removed as an
   installed *app* -- that is a different thing), it is what production uses, so
   the dev environment stops differing from production in the one way that
   matters here, and ``dev/kasvimuseo app run`` is the only place to change.
   ``runserver`` stays available for a loopback-only session.
2. **Reach the dev server over an SSH tunnel** and keep ``runserver``. No code
   changes; it is a line in the README and a habit. It also removes the
   ``ALLOWED_HOSTS = ['*']`` in ``local_settings.development.py``, which exists
   only because the server is published under an arbitrary name (issue 026).
3. **Chase the MTU** if the ``curl`` measurements point at the network rather
   than the server. ``tailscale ping --verbose`` reports the negotiated path;
   an MTU mismatch is a property of the tailnet, not of this repository.

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
issue 021 (gunicorn, which option 1 would give a real use).
