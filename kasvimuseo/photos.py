from photologue.models import Photo

from kasvimuseo.photo_matching import match_key


def get_photo_titles_pks_and_urls():
    """Every photo as its matching key, primary key and display URL.

    The key is ``photo_matching.match_key`` of the title -- the same rule the
    auto-attach receiver matches a title against ``Species.name_fi`` with, so
    the two cannot disagree about case (issue 003). A photo whose title has no
    word in it names no species and is left out rather than raising.
    """
    photos = Photo.objects.only('title', 'image').order_by('title', 'pk')
    titles_pks_and_urls = []
    for photo in photos:
        title = match_key(photo.title)
        if title is not None:
            # noinspection PyUnresolvedReferences
            titles_pks_and_urls.append(
                (title, {'pk': photo.pk, 'url': photo.get_display_url()}))
    return titles_pks_and_urls


def get_photo_pks_and_urls_by_species():
    """Get URLs of all photos, grouped by the first word of the photo title

    Accumulated into a dictionary rather than run through
    ``itertools.groupby``: the key is case-folded but the photos arrive in
    title order, so two photos sharing a key need not be adjacent --
    ``Valkonarsissi kukassa`` and ``valkonarsissi lehdet`` are not -- and
    groupby would emit two groups of which the dictionary kept only the last.
    """
    by_title = {}
    for title, pk_and_url in get_photo_titles_pks_and_urls():
        by_title.setdefault(title, []).append(pk_and_url)
    return by_title


def get_species_photos(species, photo_pks_and_urls_by_title):
    """The photos whose title names ``species``, as ``(pk, url)`` pairs.

    ``match_key`` of a blank ``name_fi`` is ``None``, which is in no dictionary
    of photos, so such a species simply has none.
    """
    return [(pk_and_url['pk'], pk_and_url['url'])
            for pk_and_url in
            photo_pks_and_urls_by_title.get(match_key(species.name_fi), [])]


def get_species_photo_info(species, photo_pks_and_urls_by_title, photo=None):
    """Return possible photos and the selected photo for the species

    :param species: The species whose photo information to get
    :type species: Species
    :param photo_pks_and_urls_by_title: Primary keys and display URLs for Photo
                                        objects, grouped by the first word of
                                        the photo title
    :type photo_pks_and_urls_by_title: dict[str, list[dict[str, int | str]]]
    :param photo: The photo chosen for this particular label, if any. It wins
                  over ``species.photo``, which is only the default for a
                  species whose label has no choice of its own (issue 039).
    :type photo: Photo | None
    :return:
    :rtype: tuple[int | None, dict[int, str]]

    """
    species_photos = get_species_photos(species, photo_pks_and_urls_by_title)
    selected_photo = photo or species.photo
    if selected_photo:
        photo_pk = selected_photo.pk
        active_photo = [(photo_pk, selected_photo.get_display_url())]
    else:
        photo_pk = None
        active_photo = []
    return photo_pk, dict(species_photos + active_photo)
