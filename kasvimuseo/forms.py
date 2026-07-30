# -*- coding: utf-8 -*-
from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from unicodedata import combining, normalize

from photologue.models import Photo

from kasvimuseo.models import Species
from kasvimuseo.photos import get_candidate_photo_pks

#: What ``clean()`` below does with the file name, and what
#: ``autoconnect_photo_to_species`` then does with the title, said to the person
#: doing the uploading (issue 037). Written in English and translated into
#: Finnish in ``locale/fi``, like every other user-facing string here; the
#: users are Finnish gardeners, so Finnish is what actually reaches the screen.
#: The admin renders ``help_text`` through ``|safe``, so the file names are
#: marked up with ``<code>`` rather than quoted.
IMAGE_HELP_TEXT = _(
    u'Name the file after the plant’s Finnish name, for example '
    u'<code>valkonarsissi.jpg</code> or <code>valkonarsissi kukassa.jpg</code>. '
    u'The photo is attached to the species whose Finnish name is the first '
    u'word of the title; upper and lower case make no difference. If no '
    u'species matches, the photo stays in the photo library and appears on no '
    u'species.')

TITLE_HELP_TEXT = _(
    u'You can leave this empty, which is the usual way: the title then becomes '
    u'the file name without the <code>jpg</code>, <code>jpeg</code> or '
    u'<code>jpe</code> extension. If you write the title yourself, begin it '
    u'with the plant’s Finnish name, because the first word of the title '
    u'is what attaches the photo to a species.')

#: The species page's own copy of the same rule, seen from the other end.
SPECIES_PHOTO_HELP_TEXT = _(
    u'The photo of this species in the plant list and in the reports. The '
    u'choices are the photos whose title begins with this plant’s Finnish '
    u'name. Empty detaches the photo from the species without deleting the '
    u'image file. Note that saving a photo in the photo library always '
    u'attaches it to its species, so saving that photo again undoes this '
    u'choice.')


def remove_diacritics(text):
    # Still ``filter()`` over a text string, which is what issue 016 is about:
    # on Python 3 this returns an iterator rather than a string. Spelled as a
    # ``def`` only because the lint forbids naming a lambda.
    return filter(lambda character: not combining(character),
                  normalize('NFKD', text))


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        exclude = []

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['title_slug'].required = False
        # The rules live in ``clean()`` below and in
        # ``models.autoconnect_photo_to_species``; this is where the person
        # uploading gets told about them (issue 037).
        self.fields['image'].help_text = IMAGE_HELP_TEXT
        self.fields['title'].help_text = TITLE_HELP_TEXT

    def clean(self):
        # ``BaseModelForm.clean()`` does one thing -- it sets the flag that
        # makes ``_post_clean()`` call ``validate_unique()`` -- so an override
        # that does not call it silently turns off uniqueness checking for the
        # whole form. ``Photo.title`` and ``Photo.title_slug`` are both unique,
        # so without this the second photo to claim a title reaches the
        # database and comes back as an ``IntegrityError``: a 500 on an upload,
        # and the image file is already written by then, leaving a file on disk
        # with no row pointing at it.
        super(PhotoForm, self).clean()
        image = self.cleaned_data.get('image')
        if not self.cleaned_data.get('title', u'').strip() and image:
            all_parts = image.name.split('.')
            parts = [part for part in all_parts
                     if part.lower() not in (u'jpg', u'jpeg', u'jpe')]
            self.cleaned_data['title'] = u' '.join(parts)
        if not self.cleaned_data.get('title_slug', u'').strip():
            self.cleaned_data['title_slug'] = slugify(remove_diacritics(
                self.cleaned_data.get('title', u'')))
        return self.cleaned_data


class SpeciesForm(forms.ModelForm):
    """The species change form, with ``photo`` as an ordinary field.

    Issue 042 made the auto-attach receiver replace a photo a species already
    has, so a photo can be *changed* by saving the one you want last -- but the
    receiver is still the only thing that ever writes ``Species.photo``, so a
    photo could not be taken off a species at all except by deleting the
    ``Photo`` row, which deletes the file for every other use of it. This is
    the small change issue 037 settled on: the field is offered here, limited
    to the photos whose title names this species, and blank detaches.
    """

    class Meta:
        model = Species

    def __init__(self, *args, **kwargs):
        super(SpeciesForm, self).__init__(*args, **kwargs)
        photo = self.fields['photo']
        photo.label = _(u'Photo')
        photo.help_text = SPECIES_PHOTO_HELP_TEXT
        pks = get_candidate_photo_pks(self.instance)
        # The photo the species has now stays on the list even if its title no
        # longer names the species, so that opening the form does not silently
        # offer to drop it.
        if self.instance.photo_id is not None:
            pks = pks + [self.instance.photo_id]
        photo.queryset = Photo.objects.filter(pk__in=pks).order_by('title')
