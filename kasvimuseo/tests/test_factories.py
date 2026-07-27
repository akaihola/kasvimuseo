# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
from kasvimuseo.tests import factories


@pytest.mark.django_db
def test_create_planted_builds_whole_chain():
    planting = factories.create_planted(cares=[5], external_id=7)
    assert planting.bed.public is True
    assert planting.observation.species.name_fi == 'valkonarsissi'
    assert planting.care_set.count() == 1


@pytest.mark.django_db
def test_photo_factory_makes_a_real_image(photo_factory):
    photo = photo_factory(width=12, height=9)
    assert photo.get_display_size() == (12, 9)
