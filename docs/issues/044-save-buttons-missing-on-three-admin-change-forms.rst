=================================================================
Issue 044: Save buttons missing on three admin change forms
=================================================================

:Status: Open
:Severity: High
:Area: admin / grappelli
:Reported: 2026-07-29
:Source: Maintainer report, ``docs/issues/incoming.rst``
:Evidence: not reproduced -- see "What has been ruled out" for the sweep
:Depends on: (none)
:Blocks: (none)
:Related: 040 -- the same three buttons, one Finnish and two English
    013 -- another admin declaration that claims something untrue
    045 -- the other report that needed a browser to settle
:Decision: undecided
:Resolution: (none yet)

Problem
=======

The whole submit row -- the dark bar carrying ``Tallenna``, ``Save and add
another`` and ``Save and continue editing`` -- does not appear on three admin
change forms:

==================== ==============================================
 Affected            ``species``, ``plot``, ``planting``
 Not affected        the other nine registered models
 Browser             Firefox 152.0.5, Linux, on an Atom laptop
 Also at the top?    No -- nothing under the heading either
 Production          Works. Production runs the 16 February 2025 code.
==================== ==============================================

Those three models cannot be edited at all in that browser, which is why this
is High. The three form a suspicious set: ``SpeciesAdmin``, ``PlotAdmin`` and
``PlantingAdmin`` are three of the four admin classes that declare ``inlines``.
The fourth is ``LocationAdmin``, reported as working -- and it is the one whose
inline set is *two* rather than one.

The bar cannot be missing from the HTML
=======================================

Grappelli's ``templates/admin/submit_line.html`` wraps the buttons in a
``<footer>`` with no condition on it at all::

    <footer class="grp-module grp-submit-row grp-fixed-footer">
        <header style="display:none"><h1>Submit Options</h1></header>
        <ul>
            {% if show_delete_link %}...{% endif %}
            {% if show_save %}...{% endif %}
            ...

Only the ``<li>`` items are conditional, and ``show_save`` is hardcoded ``True``
in Django's ``submit_row``. So the element is in every change form's response,
and whatever is happening is happening after the HTML arrives: a style, a
stylesheet that did not load, an extension, or a rendering difference in that
Firefox. That narrows the search sharply, and it is why the diagnosis below is
four things to look at in the browser rather than more code reading.

What has been ruled out
=======================

Every combination below renders the footer ``position: fixed``,
``visibility: visible``, ``opacity: 1``, at the bottom of the window, with
``elementFromPoint`` over ``Tallenna`` returning that button -- on ``species``,
``plot``, ``planting`` and ``location`` alike:

* **Both engines.** Firefox and Chromium, driven by Playwright.
* **Both databases.** A database built by the test factories, and the February
  2025 production dump restored locally -- including the objects with the most
  inline rows (``species/97`` with 12 observations, ``plot/1`` with 10 beds,
  ``planting/22`` with 9 care events).
* **Netbook-sized windows.** 1024x600, 1024x552, 800x480, 1366x768.
* **No JavaScript errors** on any of the pages.
* **The code.** Nothing between the February 2025 production release and
  ``b801d8e`` touches the change form: ``kasvimuseo/static/css/
  kasvimuseo.admin.css`` was last changed in 2011, ``kasvimuseo/admin.py`` at
  ``c10a156``, and the grappelli and photologue pins have not moved. A
  ``git bisect`` has nothing to find, so the "probably July 2026" in the
  original report is unlikely to hold.

One rule does produce exactly this symptom
------------------------------------------

Grappelli's stylesheet un-fixes the footer on small screens::

    @media only screen and (max-device-width: 600px) and (max-device-height: 600px) {
        html .grp-fixed-footer { position: static; ... }
    }

When that matches, the bar stops being fixed and lands at the end of the
document -- measured at 1497 to 2239 px down a 600 px window, i.e. invisible
unless the whole form is scrolled past. That is "the bar is gone" precisely.

It keys on the **screen**, not the window: emulating a 600x600 screen
reproduces the symptom even in a 1024-wide window, while a 1024x600 screen does
not match, because both dimensions must be at most 600. An Atom laptop is
typically 1024x600, so this should not be matching -- but it is one
``matchMedia`` call to be sure, and it is the only rule in the stack that does
this. It does not explain why three forms differ from nine, unless the nine are
short enough that the static bar was still on screen.

How to pin it down
==================

Four things, on one of the broken pages, in the Firefox that shows it:

1. **Is the element there?** Inspector, search the DOM for ``grp-submit-row``.
   It should be, per the template above. Expected: present.
2. **What is styling it?** With it selected, the Rules pane names the file and
   line of every rule that applies. Paste ``getComputedStyle(document
   .querySelector('.grp-submit-row')).position`` into the Console:
   ``fixed`` means it is being covered or scrolled away, ``static`` means the
   media query matched, ``none`` for ``display`` means something is hiding it.
3. **Is it that media query?** In the Console::

       matchMedia('(max-device-width: 600px) and (max-device-height: 600px)').matches

4. **Is it the browser or the app?** Reload with ``Ctrl+Shift+R``, then open the
   same page in a Private Window, which loads no extensions. If it comes back in
   the Private Window, an extension or a user stylesheet is hiding it and none
   of this repository's code is involved.

Also worth one line: whether the account used is a superuser, and whether the
nine working models were each opened on a *change* form rather than an *add*
form.

Fix regardless of the cause
===========================

``SpeciesAdmin``, ``PlotAdmin`` and ``PlantingAdmin`` all set
``save_on_top = True``, which in stock Django puts a second submit row directly
under the page heading -- exactly where the reporter looked and found nothing.
Grappelli drops it: its ``change_form.html`` renders ``{% submit_row %}`` once,
in ``{% block submit_buttons_bottom %}``, with no top block at all. Eight admin
classes in this project set that option and it has never done anything.

Honouring it -- a small ``templates/admin/change_form.html`` override that
extends Grappelli's and fills a top block -- puts the buttons somewhere that
does not depend on a fixed footer, on the longest forms in the application, and
would have kept these three models editable whatever is hiding the bar. That is
worth doing on its own; the alternative is to delete the eight dead
``save_on_top`` lines so the setting stops claiming something untrue.

See also
========

Issue 013 (stale ``FIXME`` comments claiming admin features are broken -- the
same admin module, the same kind of untrue declaration), issue 040 (half the
admin chrome is English -- which is why one button says ``Tallenna`` and the two
beside it do not: ``kasvimuseo/locale/fi/LC_MESSAGES/django.po`` translates
``Save`` and neither of the longer labels), issue 045 (the tablet report, where
the admin turned out to be the part that works).
