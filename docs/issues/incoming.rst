Incoming issues to be split into individual files
=================================================

For anyone who has something to report. Write it here in whatever shape it
arrives -- a sentence is enough. An agent splits it into a numbered file under
``docs/issues/``, with the causes traced as far as they go.

A report leaves this page when it becomes a numbered issue file, and it leaves
in the same commit that creates the file. Do not write down what became of it.
The issue file carries the reasoning, and ``git log -p docs/issues/incoming.rst``
carries every report this page has ever held. ``AGENTS.md`` states the rule.
:doc:`../archive` names the commit that still holds the entries this page used
to carry.

Waiting
-------

The project's ``kasvimuseo/templates/admin/change_list.html`` override is a
grappelli 2.4-era copy of grappelli's own template. Its one reason to differ
-- the ``admin_list`` fork's tag -- left with upgrade plan Stage 5, so every
remaining difference is drift: old breadcrumb URLs, an older results layout,
and none of grappelli's own fixes. Diffed again while doing upgrade plan
Stage 6, against the installed grappelli 2.7.3: 139 of the override's 244
lines differ, and the page still renders -- the admin tests pass against it.
Deleting the override would hand the page back to the installed grappelli;
the decision is still open, and grappelli moves again at Stage 7.

Production runs a newer Django than the pin. The 2026-08-26 maintenance
window's Play 1 installed GitHub ``master`` (8677c98, upgrade plan Stage 6,
which pins ``django==1.8.19``), yet the Play 2 traceback walked through
``django/contrib/auth/base_user.py`` -- a module that exists only from
Django 1.9 (the 1.8.19 wheel was checked: it has no such file) -- and the
freshly rotated password hash carries 36 000 PBKDF2 iterations, Django
1.11's constant, where 1.8 writes 20 000. So pip on the server resolved
past the pin, presumably ``pip install --upgrade``'s eager legacy resolver.
Everything observable works: the window's verify play, the outside checks
and the maintainer's click-through all passed. But the deployed tree's
grappelli 2.7.3 declares support for 1.8 only, every migration Django added
after 1.8 is unapplied on the server, and the version that actually runs
there is roughly what upgrade plan Stage 9 -- landed locally since, with
Django 1.11.29 -- pins on purpose: production got there by accident. ``pip2 freeze`` on the
server settles the exact version. The staging rehearsal of 2026-08-09
passed Play 2 with the unpatched scripts that die on 1.7 and later, so
which Django *it* installed is part of the same question.

The production ``auth_user`` table keeps three active privileged accounts
whose passwords the vault does not cover: ``hl`` (staff, in the admin as
recently as 2026-08), ``sirkku`` (a second superuser, no admin action since
2022), and ``tuula`` (staff, has never touched the admin since the account
was made in 2025). ``anja`` (staff) is inactive but keeps the flag. The
audit table in issue 050 is the evidence, and the saved Play 2 output is
the full record. Adding them to ``kasvimuseo_admin_passwords`` rotates
them; whether each keeps its account, or its flags, is the judgement the
playbook leaves to a person.
