# -*- coding: utf-8 -*-
"""What photologue 2.8's galleries do on Django 1.5.

Galleries are not something this application manages -- nothing in
``kasvimuseo`` creates one, and the photos it cares about are reached through
``Species.photo`` -- but ``/photologue/gallery/`` is a public URL this project
serves and the production database has a gallery with four photos in it.
Upgrade plan Stage 2 is where photologue starts filtering both galleries and
photos by site and ordering a gallery's photos by a sort column, which puts
three packages in one query: photologue, ``django-model-utils`` (whose
``PassThroughManager`` becomes the default manager of ``Photo`` and
``Gallery``) and ``django-sortedm2m`` (which provides ``Gallery.photos``).

They do not all compose. ``django-sortedm2m`` 1.x picks the query-set accessor
to override with ``hasattr(RelatedManager, 'get_queryset')``, meaning it to
tell Django >= 1.6 from 1.5; ``PassThroughManagerMixin`` defines
``get_queryset`` on 1.5 as well, so the test answers wrongly and the override
resolves past Django's ``ManyRelatedManager`` -- over the one method that
limits a related manager to its own instance's rows. Under sortedm2m 1.5.0
both of these fail: the first because ``gallery.photos`` is then every photo in
the database, the second with ``DatabaseError: missing FROM-clause entry for
table "photologue_gallery_photos"``, a 500 on a public page. 0.7.0, which is
what the lock pins and what photologue 2.8.3 asks for, has no such branch and
is correct here.

So these two are a bound on the pin as much as a test of photologue: they are
what fails if someone moves ``django-sortedm2m`` up while this project is still
on Django 1.5.
"""

from __future__ import unicode_literals

import pytest
from django.core.urlresolvers import reverse
from photologue.models import Gallery


@pytest.fixture
def gallery(db, photo_factory):
    gallery = Gallery.objects.create(title='Lehtoakileijat',
                                     slug='lehtoakileijat')
    gallery.photos.add(photo_factory(title='lehtoakileija kukassa'))
    return gallery


def test_a_gallery_holds_only_its_own_photos(gallery, photo_factory):
    """``gallery.photos`` has to be this gallery's photos, and no others."""
    photo_factory(title='valkonarsissi kukassa')

    assert [photo.title for photo in gallery.photos.all()] == \
        ['lehtoakileija kukassa']


def test_the_gallery_index_renders_a_gallery_that_has_photos(client, gallery):
    """``Gallery.sample()`` on the index page, which is where this shows up.

    ``sample()`` goes through ``public()``, which since 2.8 filters the photos
    by ``sites__id`` -- a second join onto a query set already ordered by the
    sort column of the gallery-photo join table, which is the combination that
    breaks.
    """
    response = client.get(reverse('pl-gallery-archive'))

    assert response.status_code == 200
    assert gallery.title in response.content.decode('utf-8')
