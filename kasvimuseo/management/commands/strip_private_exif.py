"""Remove the private EXIF tags from the stored photo originals (task 24).

``turn_photo_upright`` removes these tags from every new upload. This command
cleans the originals stored before that change. It turns no photo upright, so
the stored pixels and the label layout stay as they are.
"""

import io
import shutil
import tempfile
from pathlib import Path

from django.core.management.base import BaseCommand
from photologue.models import Photo
from PIL import Image

from kasvimuseo.models import clean_original, remove_private_tags


def replace_file(path, data):
    """Write ``data`` over the file at ``path`` in one step."""
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as new:
        new.write(data)
    try:
        shutil.copymode(path, new.name)
        Path(new.name).replace(path)
    except BaseException:
        Path(new.name).unlink(missing_ok=True)
        raise


class Command(BaseCommand):
    help = ('Remove the GPS block and the owner and serial-number tags from '
            'the stored photo originals.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', action='store_true',
            help='Only count the originals that have private tags. Change '
                 'no file.')

    def handle(self, *args, count=False, **options):
        tagged = failed = total = 0
        for photo in Photo.objects.order_by('pk').iterator():
            total += 1
            storage, name = photo.image.storage, photo.image.name
            try:
                with storage.open(name) as stored:
                    data = stored.read()
                with Image.open(io.BytesIO(data)) as image:
                    if not remove_private_tags(image.getexif()):
                        continue
                if not count:
                    replace_file(Path(storage.path(name)),
                                 clean_original(data, turn_upright=False))
            except (OSError, ValueError, Image.DecompressionBombError) as error:
                failed += 1
                self.stderr.write(f'{name}: {error}')
                continue
            tagged += 1
            if options['verbosity'] > 1:
                self.stdout.write(name)
        if count:
            self.stdout.write(f'{tagged} of {total} originals have private '
                              f'tags.')
        else:
            self.stdout.write(f'Removed the private tags from {tagged} of '
                              f'{total} originals.')
        if failed:
            self.stdout.write(f'{failed} of {total} originals failed. The '
                              f'errors above name them.')
