==============
Ylåneen kasvit
==============

A plant catalogue for the gardens of Ylåne: what is planted, where, and what has
been observed growing there. It is a Django application with two parts -- a
maintained catalogue behind the admin, and a small public site that renders it.

The catalogue
=============

The data model is in :mod:`kasvimuseo.models`:

``Species``
    The botanical record -- genus, species, subspecies, variety, Finnish name,
    height and width, spacing, flower colour, flowering months, lighting,
    substrate and cultivation history.

``Location``, ``Plot``, ``Bed``
    Where things grow, from a site down to an individual bed, with contacts
    attached to a location.

``Planting``
    A species in a bed: how many, planted when, at what distance, with a
    printable ``Label``.

``Observation``
    What was actually seen, when, and by whom -- the field record, kept separate
    from the plan.

``PlantingPhoto``, photologue ``Photo``
    Photographs, matched to species by name and served from a public media host.

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
