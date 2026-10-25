"""Tests for how a phone photo is turned upright and made private.

A phone stores a photo taken upright as a landscape image and an EXIF
``Orientation`` tag that says how to turn it. From photologue 3.20, photologue
reads the tag after it applies a ``PhotoEffect``, and an enhanced or filtered
image has no EXIF data left (upstream issue 233).

Issue 089 decided to turn each uploaded original upright before photologue
stores it. ``turn_photo_upright`` in ``kasvimuseo/models.py`` does that. The
strict expected failure at the bottom pins the upstream regression without the
receiver. It fails when a photologue release fixes the order, which is the
signal for task 19.

Task 24 made the same receiver remove the GPS block and the owner and
serial-number tags from every upload. The ``strip_private_exif`` command
removes them from the originals stored before that.
"""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL.ExifTags import GPS, IFD, Base

from kasvimuseo.tests.factories import create_species

#: The value a phone writes when it was held upright.
RIGHT_TOP = 6
TAKEN = '2026:05:01 10:00:00'
TITLE = 'valkonarsissi kukassa'


def tagged_image_bytes(orientation=RIGHT_TOP, image_format='JPEG',
                       private=False, **options):
    """A 40x20 image whose EXIF data says to turn it by ``orientation``.

    ``None`` leaves the tag out. ``private`` adds a GPS block and the
    owner and serial-number tags. ``options`` go to ``Image.save``.
    """
    from PIL import Image
    exif = Image.Exif()
    if orientation is not None:
        exif[Base.Orientation] = orientation
    details = exif.get_ifd(IFD.Exif)
    details[Base.DateTimeOriginal] = TAKEN
    if private:
        exif[Base.CameraSerialNumber] = 'KAMERA-1'
        details[Base.CameraOwnerName] = 'puutarhuri'
        details[Base.BodySerialNumber] = 'RUNKO-1'
        details[Base.LensSerialNumber] = 'LINSSI-1'
        location = exif.get_ifd(IFD.GPSInfo)
        location[GPS.GPSLatitudeRef] = 'N'
        location[GPS.GPSLatitude] = (1.0, 2.0, 3.0)
    buffer = io.BytesIO()
    Image.new('RGB', (40, 20), (0, 128, 0)).save(
        buffer, image_format, exif=exif.tobytes(), **options)
    return buffer.getvalue()


def private_tags(image):
    """The private tags that ``image`` has, of the five above."""
    exif = image.getexif()
    details = exif.get_ifd(IFD.Exif)
    return ([tag for tag in (Base.GPSInfo, Base.CameraSerialNumber)
             if tag in exif]
            + [tag for tag in (Base.CameraOwnerName, Base.BodySerialNumber,
                               Base.LensSerialNumber)
               if tag in details])


def save_photo(data, extension='jpg', effect=None, committed=True,
               title=TITLE):
    """Save a ``Photo`` the way a test or the admin uploads one.

    ``committed`` stores the file before the save, as ``photo_factory`` does.
    Otherwise the field holds the upload, as after the admin form, and
    ``FileField.pre_save`` stores it.
    """
    from photologue.models import Photo
    slug = title.replace(' ', '-')
    photo = Photo(title=title, slug=slug, effect=effect)
    name = f'{slug}.{extension}'
    upload = SimpleUploadedFile(name, data)
    if committed:
        photo.image.save(name, upload, save=False)
    else:
        photo.image = upload
    photo.save()
    return photo


def stored_bytes(photo):
    with photo.image.storage.open(photo.image.name, 'rb') as stored:
        return stored.read()


def stored_image(photo):
    from PIL import Image
    image = Image.open(io.BytesIO(stored_bytes(photo)))
    image.load()
    return image


@pytest.fixture
def without_the_receiver():
    """Disconnect ``turn_photo_upright`` for one test."""
    from django.db.models.signals import pre_save
    from photologue.models import Photo

    from kasvimuseo.models import turn_photo_upright
    assert pre_save.disconnect(turn_photo_upright, sender=Photo)
    yield
    pre_save.connect(turn_photo_upright, sender=Photo)


@pytest.mark.django_db
@pytest.mark.parametrize('committed', [True, False])
def test_a_sideways_jpeg_is_stored_upright(media_root, committed):
    species = create_species()

    photo = save_photo(tagged_image_bytes(), committed=committed)

    image = stored_image(photo)
    assert image.size == (20, 40)
    assert Base.Orientation not in image.getexif()
    assert photo.image.name == 'photologue/photos/valkonarsissi-kukassa.jpg'
    species.refresh_from_db()
    assert species.photo == photo
    assert species.photo_is_horizontal is False


@pytest.mark.django_db
def test_turning_a_stored_original_leaves_no_copy(media_root):
    photo = save_photo(tagged_image_bytes())

    assert photo.image.storage.listdir('photologue/photos')[1] == [
        'valkonarsissi-kukassa.jpg']


@pytest.mark.django_db
def test_the_stored_original_keeps_the_date_taken(media_root):
    photo = save_photo(tagged_image_bytes())

    exif = stored_image(photo).getexif().get_ifd(IFD.Exif)
    assert exif[Base.DateTimeOriginal] == TAKEN
    assert photo.date_taken is not None


@pytest.mark.django_db
@pytest.mark.parametrize('orientation', [1, None])
@pytest.mark.parametrize('image_format, extension', [
    ('PNG', 'png'),
    ('JPEG', 'jpg'),
])
def test_an_upright_image_is_stored_as_uploaded(
        media_root, image_format, extension, orientation):
    data = tagged_image_bytes(orientation, image_format)

    photo = save_photo(data, extension)

    assert stored_bytes(photo) == data


@pytest.mark.django_db
def test_a_sideways_photo_with_no_effect_is_shown_upright(
        media_root, display_size):
    assert save_photo(tagged_image_bytes()).get_display_size() == (20, 40)


@pytest.mark.django_db
def test_a_sideways_photo_with_an_effect_is_shown_upright(
        media_root, display_size):
    from photologue.models import PhotoEffect
    effect = PhotoEffect.objects.create(name='kontrasti', contrast=1.2)

    photo = save_photo(tagged_image_bytes(), effect=effect)

    assert photo.get_display_size() == (20, 40)


@pytest.mark.django_db
def test_a_sideways_photo_with_a_size_effect_is_shown_upright(
        media_root, display_size):
    from photologue.models import PhotoEffect, PhotoSize
    size = PhotoSize.objects.get(name='display')
    size.effect = PhotoEffect.objects.create(name='kontrasti', contrast=1.2)
    size.save()

    photo = save_photo(tagged_image_bytes())

    assert photo.get_display_size() == (20, 40)


@pytest.mark.django_db
@pytest.mark.xfail(strict=True, reason='upstream issue 233')
def test_photologue_turns_a_photo_with_an_effect_upright(
        media_root, display_size, without_the_receiver):
    """The regression of issue 089, which the receiver works around.

    Photologue 3.19 passed this test. When a photologue release passes it
    again, the strict mark fails the suite. Task 19 then decides whether the
    receiver can go.
    """
    from photologue.models import PhotoEffect
    effect = PhotoEffect.objects.create(name='kontrasti', contrast=1.2)

    photo = save_photo(tagged_image_bytes(), effect=effect)

    assert photo.get_display_size() == (20, 40)


# Task 24: the private tags.


@pytest.mark.django_db
@pytest.mark.parametrize('orientation, size', [
    (RIGHT_TOP, (20, 40)),
    (1, (40, 20)),
    (None, (40, 20)),
])
@pytest.mark.parametrize('committed', [True, False])
def test_an_upload_is_stored_without_private_tags(
        media_root, orientation, size, committed):
    from PIL import Image
    data = tagged_image_bytes(orientation, private=True)
    assert len(private_tags(Image.open(io.BytesIO(data)))) == 5

    photo = save_photo(data, committed=committed)

    image = stored_image(photo)
    assert private_tags(image) == []
    assert image.getexif().get_ifd(IFD.GPSInfo) == {}
    assert image.getexif().get_ifd(IFD.Exif)[Base.DateTimeOriginal] == TAKEN
    assert photo.date_taken is not None
    assert image.size == size
    assert photo.image.storage.listdir('photologue/photos')[1] == [
        'valkonarsissi-kukassa.jpg']


@pytest.mark.django_db
def test_a_png_upload_is_stored_without_private_tags(media_root):
    photo = save_photo(tagged_image_bytes(None, 'PNG', private=True), 'png')

    image = stored_image(photo)
    assert image.format == 'PNG'
    assert private_tags(image) == []
    assert image.getexif().get_ifd(IFD.Exif)[Base.DateTimeOriginal] == TAKEN


@pytest.mark.django_db
@pytest.mark.parametrize('image_format', ['JPEG', 'MPO'])
def test_a_cleaned_jpeg_keeps_its_quality_and_colour_profile(
        media_root, image_format):
    from PIL import Image, JpegImagePlugin
    options = {}
    if image_format == 'MPO':
        # A phone photo with a second image, for example a gain map.
        options = {'save_all': True,
                   'append_images': [Image.new('RGB', (40, 20))]}
    data = tagged_image_bytes(
        None, image_format, private=True, quality=95, subsampling=0,
        icc_profile=b'synthetic profile', **options)
    uploaded = Image.open(io.BytesIO(data))
    assert uploaded.format == image_format

    image = stored_image(save_photo(data))

    assert private_tags(image) == []
    assert image.format == 'JPEG'
    assert image.quantization == uploaded.quantization
    assert JpegImagePlugin.get_sampling(image) == 0
    assert image.info['icc_profile'] == b'synthetic profile'


@pytest.mark.django_db
def test_an_image_with_too_many_pixels_is_refused(media_root, monkeypatch):
    """The receiver's error for a save outside the admin form.

    The 40x20 image has 800 pixels, more than twice the limit of 100, so
    Pillow raises ``DecompressionBombError``.
    """
    from django.core.exceptions import ValidationError
    from photologue.models import Photo
    from PIL import Image

    from kasvimuseo.models import TOO_MANY_PIXELS
    monkeypatch.setattr(Image, 'MAX_IMAGE_PIXELS', 100)

    with pytest.raises(ValidationError) as refused:
        save_photo(tagged_image_bytes(None, private=True), committed=False)

    assert refused.value.message_dict == {'image': [str(TOO_MANY_PIXELS)]}
    assert not Photo.objects.exists()


# Task 24: the command for the stored originals.


@pytest.fixture
def stored_originals(media_root, without_the_receiver):
    """Two originals as stored before task 24, one with private tags."""
    return (save_photo(tagged_image_bytes(private=True)),
            save_photo(tagged_image_bytes(1), title='tarhapioni kukassa'))


def strip_private_exif(*args, **options):
    """Run the command. Return what it wrote to stdout and stderr."""
    from django.core.management import call_command
    stdout, stderr = io.StringIO(), io.StringIO()
    call_command('strip_private_exif', *args, stdout=stdout, stderr=stderr,
                 **options)
    return stdout.getvalue(), stderr.getvalue()


@pytest.mark.django_db
def test_the_count_mode_counts_the_tagged_originals_and_changes_nothing(
        stored_originals):
    before = [stored_bytes(photo) for photo in stored_originals]

    assert strip_private_exif('--count') == (
        '1 of 2 originals have private tags.\n', '')
    assert [stored_bytes(photo) for photo in stored_originals] == before


@pytest.mark.django_db
def test_the_command_names_the_tagged_originals_on_request(
        stored_originals):
    stdout, _ = strip_private_exif('--count', verbosity=2)

    assert stdout.splitlines() == [
        'photologue/photos/valkonarsissi-kukassa.jpg',
        '1 of 2 originals have private tags.']


@pytest.mark.django_db
def test_the_command_removes_the_private_tags_and_turns_nothing(
        stored_originals):
    tagged, clean = stored_originals
    clean_before = stored_bytes(clean)

    assert strip_private_exif() == (
        'Removed the private tags from 1 of 2 originals.\n', '')

    image = stored_image(tagged)
    assert private_tags(image) == []
    assert image.getexif().get_ifd(IFD.Exif)[Base.DateTimeOriginal] == TAKEN
    assert image.getexif()[Base.Orientation] == RIGHT_TOP
    assert image.size == (40, 20)
    assert stored_bytes(clean) == clean_before
    assert sorted(tagged.image.storage.listdir('photologue/photos')[1]) == [
        'tarhapioni-kukassa.jpg', 'valkonarsissi-kukassa.jpg']
    assert strip_private_exif('--count')[0] == (
        '0 of 2 originals have private tags.\n')


@pytest.mark.django_db
def test_the_command_reports_an_original_it_cannot_read(stored_originals):
    tagged, clean = stored_originals
    clean.image.storage.delete(clean.image.name)

    stdout, stderr = strip_private_exif('--count')

    assert stdout.splitlines() == [
        '1 of 2 originals have private tags.',
        '1 of 2 originals failed. The errors above name them.']
    assert clean.image.name in stderr
