# -*- coding: utf-8 -*-
"""Tests for the project's own template filters."""

from __future__ import unicode_literals

import pytest
from django.utils.dates import MONTHS

from kasvimuseo.models import LIGHTINGS_VERBOSE, Observation
from kasvimuseo.templatetags.bush import bush_shadow
from kasvimuseo.templatetags.kasvimuseo_model_tags import (external_ids,
                                                           nicknames)
from kasvimuseo.templatetags.kasvimuseo_photo_tags import get_photo_orientation
from kasvimuseo.templatetags.lightings import lighting_name
from kasvimuseo.templatetags.months import month_name
from kasvimuseo.tests import factories


@pytest.mark.parametrize('number', sorted(MONTHS))
def test_month_name_returns_the_localised_name(number):
    assert month_name(number) == MONTHS[number]


@pytest.mark.parametrize('number', [0, None])
def test_month_name_of_a_falsy_number_is_empty(number):
    assert month_name(number) == ''


@pytest.mark.parametrize('number,expected', LIGHTINGS_VERBOSE)
def test_lighting_name_returns_the_verbose_name(number, expected):
    assert lighting_name(number) == expected


@pytest.mark.parametrize('number', [0, None])
def test_lighting_name_of_a_falsy_number_is_empty(number):
    assert lighting_name(number) == ''


class FakePlanting(object):
    def __init__(self, width, depth):
        self.width = width
        self.depth = depth


@pytest.mark.parametrize('width,depth,expected', [
    # The narrower dimension is subtracted from both and becomes the shadow
    # radius, so a square planting is drawn as a point with a wide shadow.
    (4, 10, 'width: 0em;height: 6em;left: 2.0em;top: 2.0em;'
            'box-shadow: 0px 0px 2.0em 2.0em rgba(0, 255, 0, 1);'),
    (10, 4, 'width: 6em;height: 0em;left: 2.0em;top: 2.0em;'
            'box-shadow: 0px 0px 2.0em 2.0em rgba(0, 255, 0, 1);'),
    (5, 5, 'width: 0em;height: 0em;left: 2.5em;top: 2.5em;'
           'box-shadow: 0px 0px 2.5em 2.5em rgba(0, 255, 0, 1);'),
])
def test_bush_shadow(width, depth, expected):
    assert bush_shadow(FakePlanting(width, depth)) == expected


@pytest.mark.django_db
def test_nicknames_skips_the_observations_without_one():
    factories.create_observation(nickname='Mummon')
    factories.create_observation(nickname='')
    factories.create_observation(nickname='Naapurin')
    assert sorted(nicknames(Observation.objects.all())) == ['Mummon',
                                                            'Naapurin']


@pytest.mark.django_db
def test_external_ids_are_sorted():
    for external_id in (30, 10, 20):
        factories.create_observation(external_id=external_id)
    assert external_ids(Observation.objects.all()) == [10, 20, 30]


class FakePhoto(object):
    def __init__(self, width, height):
        self.size = (width, height)

    def get_display_size(self):
        return self.size


@pytest.mark.parametrize('width,height,expected', [
    (3, 4, 'vertical'),          # 0.75, just under the 3.1/4.0 threshold
    (4, 3, 'horizontal'),
    (3.1, 4.0, 'horizontal'),    # exactly on the threshold
])
def test_get_photo_orientation(width, height, expected):
    assert get_photo_orientation(FakePhoto(width, height)) == expected
