==========
Kasvimuseo
==========

A catalogue of heritage garden plants: where a plant was found, who grew it,
what it is, and which bed it now lives in. The ``kasvimuseo`` application runs
two sites from one codebase -- *Yläneen perinnekasvit* and *Kajalan kasvimaat*,
each with its own settings module, database and media host. Most of the work
happens in the Django admin; a handful of public pages render the result.

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
    from a public media host; see issues 002 and 003 for the sharp edges in that.

The public site
===============

A handful of views under :mod:`kasvimuseo.views`: the list of planted species,
a printable and a compact variant of it, per-observation pages, planting labels
and a bed map. The project configuration -- settings, URLs, the Grappelli admin
dashboard -- lives in :mod:`ylaneenkasvit`.

Running it
==========

The application is Django 1.5 on Python 2.7, so it runs in a container with a
throwaway PostgreSQL cluster beside it. One script drives everything::

    $ dev/kasvimuseo app build
    $ dev/kasvimuseo db bootstrap
    $ dev/kasvimuseo app run

:doc:`development` has the rest: production dumps, media, tests, and the Ansible
deployment.

The state of the code
=====================

That runtime is end of life. :doc:`issues/036-the-runtime-stack-is-end-of-life`
is the umbrella issue, :doc:`upgrade-plan` is the twenty-stage route out of it,
and :doc:`issues/index` is everything else known to be wrong, one file per
problem, each with a status.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   development
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
