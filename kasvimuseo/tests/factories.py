# -*- coding: utf-8 -*-
"""Builders for the Plot/Bed/Location/Species/Observation/Planting/Care graph.

The public-visibility rules are what most of the suite tests, so the builders
make the states those rules turn on -- a private bed, a removed planting, a
planting cared down to zero -- easy to ask for by keyword.
"""

from __future__ import unicode_literals

import datetime

from kasvimuseo import models

PLANTING_DATE = datetime.date(2020, 5, 1)
OBSERVATION_DATE = datetime.date(2020, 1, 1)


def create_plot(name='Piha', **kwargs):
    return models.Plot.objects.create(name=name, **kwargs)


def create_bed(name='1', public=True, plot=None, **kwargs):
    return models.Bed.objects.create(name=name, public=public, plot=plot,
                                     **kwargs)


def create_location(name='Talo', **kwargs):
    return models.Location.objects.create(name=name, **kwargs)


def create_species(name_fi='valkonarsissi', **kwargs):
    kwargs.setdefault('type', 2)
    kwargs.setdefault('genus', 'Narcissus')
    kwargs.setdefault('species', 'poeticus')
    return models.Species.objects.create(name_fi=name_fi, **kwargs)


def create_observation(species=None, origin=None, **kwargs):
    kwargs.setdefault('date', OBSERVATION_DATE)
    return models.Observation.objects.create(
        species=species or create_species(),
        origin=origin or create_location(),
        **kwargs)


def create_planting(observation=None, bed=None, count=3, **kwargs):
    kwargs.setdefault('planting_date', PLANTING_DATE)
    return models.Planting.objects.create(
        observation=observation or create_observation(),
        bed=bed if bed is not None else create_bed(),
        count=count,
        **kwargs)


def create_care(planting, count=0, date=None, description='harvennus'):
    return models.Care.objects.create(
        planting=planting,
        date=date or PLANTING_DATE + datetime.timedelta(days=30),
        description=description,
        count=count)


def create_planted(public=True, removed=False, cares=(), species=None,
                   bed=None, name_fi='valkonarsissi', external_id=None,
                   nickname='', **planting_kwargs):
    """Build a whole species-to-planting chain and return the ``Planting``.

    :param public: whether the bed the planting sits in is public
    :param removed: whether to set the planting's ``removal_date``
    :param cares: ``count`` values for the care operations to attach, oldest
                  first; each is dated a further month after the planting
    """
    species = species or create_species(name_fi=name_fi,
                                        external_id=external_id)
    observation = create_observation(species=species,
                                     external_id=external_id,
                                     nickname=nickname)
    planting = create_planting(
        observation=observation,
        bed=bed if bed is not None else create_bed(public=public),
        removal_date=PLANTING_DATE + datetime.timedelta(days=365)
                     if removed else None,
        **planting_kwargs)
    for month, count in enumerate(cares, start=1):
        create_care(planting, count=count,
                    date=PLANTING_DATE + datetime.timedelta(days=30 * month))
    return planting
