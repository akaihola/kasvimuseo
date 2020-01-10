from django import forms
from django.template.defaultfilters import slugify
from unicodedata import combining, normalize

from photologue.models import Photo


remove_diacritics = lambda u: filter(lambda x: not combining(x),
                                     normalize('NFKD', u))


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        exclude = []

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['title_slug'].required = False

    def clean(self):
        if not self.cleaned_data.get('title', u'').strip():
            all_parts = self.cleaned_data['image'].name.split('.')
            parts = [part for part in all_parts
                     if part.lower() not in (u'jpg', u'jpeg', u'jpe')]
            self.cleaned_data['title'] = u' '.join(parts)
        if not self.cleaned_data.get('title_slug', u'').strip():
            self.cleaned_data['title_slug'] = slugify(remove_diacritics(
                self.cleaned_data['title']))
        return self.cleaned_data
