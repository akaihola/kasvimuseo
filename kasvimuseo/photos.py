from itertools import groupby

from photologue.models import Photo


def get_photo_titles_pks_and_urls():
    photos = Photo.objects.only('title', 'image').order_by('title', 'pk')
    # noinspection PyUnresolvedReferences
    return [(photo.title.split()[0].lower(),
             {'pk': photo.pk, 'url': photo.get_display_url()})
            for photo in photos]


def get_photo_pks_and_urls_by_species():
    """Get URLs of all photos, grouped by the first word of the photo title"""
    # noinspection PyUnresolvedReferences
    all_photos = get_photo_titles_pks_and_urls()
    titles_pks_and_urls = groupby(all_photos, lambda (title, _): title)
    return {title: [pk_and_url for _, pk_and_url in pks_and_urls]
            for title, pks_and_urls in titles_pks_and_urls}


def get_species_photos(species, photo_pks_and_urls_by_title):
    return [(pk_and_url['pk'], pk_and_url['url'])
            for pk_and_url in
            photo_pks_and_urls_by_title.get(species.name_fi.split()[0], [])]


def get_species_photo_info(species, photo_pks_and_urls_by_title):
    """Return possible photos and the selected photo for the species

    :param species: The species whose photo information to get
    :type species: Species
    :param photo_pks_and_urls_by_title: Primary keys and display URLs for Photo
                                        objects, grouped by the first word of
                                        the photo title
    :type photo_pks_and_urls_by_title: dict[str, list[dict[str, int | str]]]
    :return:
    :rtype: tuple[int | None, dict[int, str]]

    """
    species_photos = get_species_photos(species, photo_pks_and_urls_by_title)
    if species.photo:
        photo_pk = species.photo.pk
        active_photo = [(photo_pk, species.photo.get_display_url())]
    else:
        photo_pk = None
        active_photo = []
    return photo_pk, dict(species_photos + active_photo)
