from django import forms
from django.template.defaultfilters import slugify
from unicodedata import combining, normalize

from photologue.models import Photo


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
