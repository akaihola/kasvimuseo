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
and none of grappelli 2.6's own fixes. Diffed against the installed grappelli
2.6.5 while doing Stage 5. Deleting the override would hand the page back to
the installed grappelli; decide at Stage 6, where grappelli moves again.
