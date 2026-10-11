==========
Kasvimuseo
==========

This documentation helps developers understand and change the plant catalogue.
The Django administration pages manage records, and public pages display the collection.
Private site configuration and operations records live in the separate deployment repository.

Provenance, not just plants
===========================

The data model in :mod:`kasvimuseo.models` is built around where a plant came
from, which is what makes it a *museum* rather than a plant list:

``Species``
    The botanical record -- genus, species, subspecies, variety, Finnish name,
    height and width, spacing, flower colour, flowering months, lighting,
    substrate and cultivation history.

``Location``, ``Contact``
    A place a plant was collected from -- village, area, address, its history --
    and the people connected to it.

``Observation``
    One specimen, recorded at its ``origin`` location: the species, the date, the
    variation, what it looked like, the stories told about it, and the nickname
    it was known by. This, not ``Species``, is what gets planted.

``Plot``, ``Bed``
    The growing area the collection is kept in, a bed at a time. A bed can be
    marked ``public``, which is what the public pages list.

``Planting``
    An observation planted in a bed: how many, planted when, at what distance
    from the left and the front, how wide and deep it grew, when it was removed,
    and the printable ``Label`` it carries.

``Care``
    What was done to a planting, and when.

``PlantingPhoto``, photologue ``Photo``
    Photographs. Photologue photos are matched to species by filename and served
    from a public media host; see issues 002, 003, 037 and 039 for the sharp
    edges in that. ``PlantingPhoto`` is declared but used nowhere.

The public site
===============

A handful of views under :mod:`kasvimuseo.views`: the list of planted species,
a printable and a compact variant of it, per-observation pages, planting labels
and a bed map. The project configuration -- settings, URLs, the Grappelli admin
dashboard -- lives in :mod:`ylaneenkasvit`.

Running it
==========

The application is Django 6.0 on Python 3.13, and it runs in a container with a
throwaway PostgreSQL cluster beside it. One script drives everything::

    $ dev/kasvimuseo app build
    $ dev/kasvimuseo db bootstrap
    $ dev/kasvimuseo app run

:doc:`development` has the rest: database restores, media, tests, and how these
pages are built and served. The private deployment repository owns the
deployment instructions.

The state of the code
=====================

The runtime upgrade programme is complete.
:doc:`issues/036-the-runtime-stack-is-end-of-life` is its closed umbrella issue,
:doc:`upgrade-plan` records the twenty stages that reached Django 6.0, and
:doc:`issues/index` is everything else known to be wrong, one file per problem,
each with a status.

To pick up work rather than read about it, start at
:doc:`issues/next`: the ranked queue of what is actionable today, generated
from those statuses, with the few facts about branch, tests and documentation
build that a fresh session needs. If this is your first change here,
:doc:`your-first-change` is that queue with the surrounding sequence spelled
out -- what the words mean, what to run, and what a finished change looks like.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   your-first-change
   development
   user-guide
   issues/index

.. toctree::
   :maxdepth: 1
   :caption: Plans and analyses

   upgrade-plan
   dependency-inventory
   test-coverage-plan

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
   third-party-notices
   archive
