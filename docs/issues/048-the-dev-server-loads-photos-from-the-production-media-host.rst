======================================================================
Issue 048: The dev server loads photos from the production media host
======================================================================

:Status: Open
:Severity: Medium
:Area: dev environment / media
:Reported: 2026-07-29
:Source: Maintainer report
:Evidence: (none -- ``ylaneenkasvit/test_settings.py`` sets ``MEDIA_URL = '/media/'``, so no test sees the development value)
:Depends on: (none)
:Blocks: (none)
:Related: 044 -- the other dev-environment report, from the same machine pair
    011 -- the views that need the image files present locally, and the
    reason ``media fetch`` exists
    028 -- the derived sizes, which are generated locally but addressed
    remotely
    042 -- replacing a species photo, which is photo work done in development
:Decision: undecided -- the current behaviour is deliberate (see "Why it is
    like this"), so this is a request to change a design rather than a repair.
    Which of the three options below is taken wants a ruling, and option 3
    changes what ``dev/kasvimuseo media fetch`` has to be told.
:Resolution: (none yet)

Problem
=======

``dev/kasvimuseo app run`` on ``gogo``, browsed from another machine over the
tailnet at ``http://gogo.crane-boa.ts.net:8000/photologue/photo/isoritarinkannus-123-tottila/``,
renders its photo as::

    http://media.kasvit.ambitone.com/photologue/photos/IMG_2272_linkedin.jpeg

The page comes from the development server; the picture on it comes from
production. Nothing under ``http://gogo.crane-boa.ts.net:8000/`` serves photos
at all.

Two settings put it there, and both are working as written.

**The URL.** ``ylaneenkasvit/local_settings.development.py`` points ``MEDIA_URL``
at the production media host, protocol-relative::

    settings['MEDIA_ROOT'] = os.path.join(settings['PROJECT_ROOT'], 'media')
    settings['MEDIA_URL'] = '//media.kasvit.ambitone.com/'
    #MEDIA_URL = '/media/'

Every photo URL is built from that: ``photo.image.url`` for the original, and
photologue's ``cache_url()`` -- ``dirname(self.image.url) + '/cache'`` -- for
every derived size behind ``get_display_url()``. The leading ``//`` means the
browser copies the scheme of the page it is on, which is why a page served over
plain HTTP asks for the image over plain HTTP.

**The route.** Nothing serves ``MEDIA_ROOT``. ``ylaneenkasvit/urls.py`` has one
static route and it is for grappelli's own media (issue 022 wants that one
deleted). ``runserver`` under ``django.contrib.staticfiles`` wraps the handler
in ``StaticFilesHandler``, whose ``get_base_url()`` returns ``STATIC_URL`` and
nothing else -- Django has never served ``MEDIA_URL`` from ``runserver`` by
itself; that is what ``django.conf.urls.static.static()`` is for, and this
project does not call it.

So the local ``media/`` directory that ``dev/kasvimuseo media fetch`` fills is
readable by Django and unreachable by the browser.

Why it is like this
===================

It is deliberate, and ``README.rst`` says so::

    Photos are loaded straight from ``media.kasvit.ambitone.com``, so the species
    list, the planting labels and the admin need no local media.

The media host is public, so pointing a fresh clone at it means photos appear
without a 260 MB download and without SSH to production. ``media fetch`` exists
only because two views -- the printable and compact species reports -- open the
image files to read their dimensions (issue 011), which a URL cannot satisfy.

That trade was made for a developer browsing on the machine the server runs on,
with the public internet available. This report is from the setup 044 also came
from: server on ``gogo``, browser on another machine over the tailnet.

Impact
======

Photos still display, as long as the browsing machine can reach the public
internet, so this is not a broken page today. What it costs:

* **Development photo work does not work.** A photo uploaded or replaced in the
  development admin is written to the local ``MEDIA_ROOT``; its URL names
  production, which has never heard of the file, so it 404s. That is the whole
  of issue 042's subject matter, and 043's changelist thumbnails.
* **Locally generated sizes are addressed remotely.** ``media fetch`` downloads
  originals only; the derived sizes are created on demand into the local
  ``cache/`` directory (this is the mechanism issue 028 is about). Their URLs
  point at production's ``cache/``, so what the browser gets is whatever
  production generated -- and any photosize production does not have is a 404
  no local file can fill.
* **The fetched copy is never the one shown.** After ``media fetch`` the same
  bytes exist locally, and the browser still asks production for them. A dump
  restored at one date and a media host at another disagree silently.
* **No offline development, and no isolation.** The dev server needs a route to
  the public internet from the *browser's* machine, not just the server's, and
  every dev page view is a request to the production host.

Options
=======

1. **Serve the local media and stop naming production.** In the development
   settings, ``settings['MEDIA_URL'] = '/media/'``; in ``urls.py``, under
   ``DEBUG``, add ``static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)``.
   Correct and self-contained, but it makes ``media fetch`` a prerequisite for
   seeing any photo at all rather than for two reports, which is the 260 MB the
   current design avoids.
2. **Make it switchable.** Keep the production host as the default and let
   ``KASVIMUSEO_MEDIA_URL`` override it, alongside the ``KASVIMUSEO_DB_*``
   variables ``dev/kasvimuseo`` already passes through. Cheapest, and it leaves
   the fresh-clone experience alone -- but the developer has to know the switch
   exists, and a switch left in the wrong position is exactly the confusion
   reported here.
3. **Local first, production as fallback.** Serve ``/media/`` from
   ``MEDIA_ROOT`` and, when the file is not there, redirect to
   ``https://media.kasvit.ambitone.com/`` + the same path. Everything the
   database already references keeps working with no download, uploads and
   locally generated sizes work because they exist locally, and the page never
   names production. It is the only option that fixes the impacts above without
   requiring ``media fetch`` first; it costs a small view, and it is one more
   thing that behaves differently from production.

Traps for whoever takes it
==========================

* **The commented-out line is dead.** ``#MEDIA_URL = '/media/'`` sits inside
  ``def modify(settings)``. Uncommented, it assigns a local variable and
  changes nothing -- every other line in that function writes into
  ``settings[...]``. It reads like a one-character fix and is not one.
* **``media fetch`` downloads from ``settings.MEDIA_URL``.** Options 1 and 3
  take that away from it: it would start fetching from the dev server it is
  meant to fill. The public host has to become its own constant in
  ``dev/kasvimuseo`` first, in the same change.
* **``README.rst`` states the current design** in the paragraph quoted above,
  and ``local_settings.development.py`` states it in a comment. Both are part
  of whichever option is taken.
* **Production is untouched by all three.** ``ylaneenkasvit_settings.py`` keeps
  ``MEDIA_URL = '//media.kasvit.ambitone.com/'``; only the development settings
  and the URL configuration change, and the ``urls.py`` route must be inside a
  ``if settings.DEBUG:`` guard so it cannot serve files on the real server.
