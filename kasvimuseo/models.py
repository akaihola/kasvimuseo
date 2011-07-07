# -*- coding: utf-8 -*-

from django.db import models
from django.utils.dates import MONTHS
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _


PLANT_TYPE_CHOICES = ((1, u'Yksi/kaksiv. koristekasvi'),
                      (2, u'Perenna'),
                      (3, u'Yrtti'),
                      (4, u'Muu hyötykasvi'),
                      (5, u'Koristepensas'),
                      (6, u'Koristeköynnös'),
                      (7, u'Marja'),
                      (8, u'Marjapensas'),
                      (9, u'Koristepuu'),
                      (10, u'Hedelmäpuu'))


ROMAN_NUMERALS = ('',
                  'I', 'II', 'III', 'IV', 'V', 'VI',
                  'VII', 'VIII', 'IX', 'X', 'XI', 'XII')
ROMAN_TO_INT = dict((unicode(roman), index or None)
                    for index, roman in enumerate(ROMAN_NUMERALS))
INT_TO_ROMAN = dict((index + 1, unicode(roman))
                     for index, roman in enumerate(ROMAN_NUMERALS[1:]))


class Species(models.Model):
    external_id = models.IntegerField(
        verbose_name=_(u'LajiNro'),
        null=True, blank=True)
    type = models.IntegerField(
        choices=PLANT_TYPE_CHOICES,
        verbose_name=_(u'type'))
    genus = models.CharField(
        max_length=40,
        verbose_name=_(u'Sukunimi'))
    group = models.CharField(
        max_length=40,
        verbose_name=_(u'Ryhmä'),
        blank=True)
    species = models.CharField(
        max_length=40,
        verbose_name=_(u'Laji'))
    subspecies = models.CharField(
        max_length=40,
        verbose_name=_(u'subspecies'),
        blank=True)
    variety = models.CharField(
        max_length=40,
        verbose_name=_(u'lajike'),
        blank=True)
    name_fi = models.CharField(
        max_length=40,
        verbose_name=_(u'SuomalainenNimi'))
    height = models.CharField(
        max_length=40,
        verbose_name=_(u'korkeuscm'),
        blank=True)
    width = models.CharField(
        max_length=40,
        verbose_name=_(u'leveyscm'),
        blank=True)
    spacing = models.TextField(
        verbose_name=_(u'Taimiväli'),
        blank=True)
    flower_color = models.CharField(
        max_length=80,
        verbose_name=_(u'kukinnanväri'),
        blank=True)
    flowering_start = models.IntegerField(
        verbose_name=_(u'first flowering month'),
        choices=MONTHS.items(),
        null=True, blank=True)
    flowering_end = models.IntegerField(
        verbose_name=_(u'last flowering month'),
        choices=MONTHS.items(),
        null=True, blank=True)
    substrate = models.TextField(
        verbose_name=_(u'Kasvualusta'),
        blank=True)

    def __unicode__(self):
        return self.name_fi

    def name_with_subspecies(self):
        if self.subspecies:
            return u'%s/%s' % (self.name_fi, self.subspecies)
        return self.name_fi

    def flowering_time(self):
        if self.flowering_start is None:
            return u''
        start = INT_TO_ROMAN[self.flowering_start]
        if self.flowering_end is None:
            return start
        return u'%s–%s' % (start, INT_TO_ROMAN[self.flowering_end])
    flowering_time.short_description = _(u'flowering time')

    class Meta:
        verbose_name = _(u'(one) species')
        verbose_name_plural = _(u'(all) species')
        ordering = 'name_fi',


class Contact(models.Model):
    last_name = models.CharField(
        max_length=40,
        verbose_name=_(u'SukuNimi'))
    first_name = models.CharField(
        max_length=40,
        verbose_name=_(u'EtuNimi'))
    phone = models.CharField(
        max_length=40,
        verbose_name=_(u'LankaPuh'),
        blank=True)
    mobile = models.CharField(
        max_length=40,
        verbose_name=_(u'MatkaPuh'),
        blank=True)
    email = models.EmailField(
        verbose_name=_(u'SähköPosti'),
        blank=True)
    street = models.CharField(
        max_length=80,
        verbose_name=_(u'KatuOsoite'),
        blank=True)
    number = models.CharField(
        max_length=20,
        verbose_name=_(u'N:o'),
        blank=True)
    apartment = models.CharField(
        max_length=20,
        verbose_name=_(u'as'),
        blank=True)
    zipcode = models.CharField(
        max_length=5,
        verbose_name=_(u'PostiNro'),
        blank=True)
    city = models.CharField(
        max_length=40,
        verbose_name=_(u'PostiToimiPaikka'),
        blank=True)
    description = models.TextField(
        verbose_name=_(u'Lisätieto'),
        blank=True)

    def __unicode__(self):
        return u'%s, %s' % (self.last_name, self.first_name)

    class Meta:
        verbose_name = _(u'contact')
        verbose_name_plural = _(u'contacts')
        ordering = 'last_name',


class Location(models.Model):
    external_id = models.IntegerField(
        verbose_name=_(u'YhteysNro'),
        null=True, blank=True)
    name = models.CharField(
        max_length=40,
        verbose_name=_(u'Talo'))
    alias = models.CharField(
        max_length=40,
        verbose_name=_(u'Toinen nimitys'),
        blank=True)
    village = models.CharField(
        max_length=40,
        verbose_name=_(u'Kylä'),
        blank=True)
    area = models.CharField(
        max_length=40,
        verbose_name=_(u'Asuinalue'),
        blank=True)
    street = models.CharField(
        max_length=80,
        verbose_name=_(u'KatuOsoite'),
        blank=True)
    number = models.CharField(
        max_length=20,
        verbose_name=_(u'N:o'),
        blank=True)
    apartment = models.CharField(
        max_length=20,
        verbose_name=_(u'as'),
        blank=True)
    zipcode = models.CharField(
        max_length=5,
        verbose_name=_(u'PostiNro'),
        blank=True)
    city = models.CharField(
        max_length=40,
        verbose_name=_(u'PostiToimiPaikka'),
        blank=True)
    history = models.TextField(
        verbose_name=_(u'Historia'),
        help_text=_(u'Tietoja talon ja puutarhan historiasta'),
        blank=True)
    contacts = models.ManyToManyField(
        Contact,
        through='LocationContact')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'location')
        verbose_name_plural = _(u'locations')
        ordering = 'name',


class LocationContact(models.Model):
    location = models.ForeignKey(Location)
    contact = models.ForeignKey(Contact)

    def __unicode__(self):
        return u'%s/%s' % (self.location, self.contact)

    class Meta:
        verbose_name = _(u'contact for location')
        verbose_name_plural = _(u'contacts for locations')
        unique_together = ('location', 'contact'),
        db_table = 'kasvimuseo_location_contacts'  # default for ManyToMany


def get_next_observation_extid():
    last_id = (Observation.objects
               .order_by('-external_id')
               .values_list('external_id', flat=True)[0])
    return _(u'Next available ID: %s') % (last_id + 1)
get_next_observation_extid = lazy(get_next_observation_extid, unicode)


class Observation(models.Model):
    external_id = models.IntegerField(
        null=True, blank=True,
        verbose_name=_(u'YläneNro'),
        help_text=get_next_observation_extid())
    origin = models.ForeignKey(
        Location,
        verbose_name=_(u'Kasvin alkuperä'))
    species = models.ForeignKey(
        Species,
        verbose_name=_(u'Kasvilaji'))
    variation = models.CharField(
        max_length=200,
        verbose_name=_(u'color/form'),
        blank=True)
    date = models.DateField(
        verbose_name=_(u'Havaintopäivä'))
    characteristics = models.TextField(
        verbose_name=_(u'Tuntomerkkejä'),
        help_text=_(u'Miltä se näyttää?'),
        blank=True)
    nickname = models.CharField(
        max_length=200,
        verbose_name=_(u'Kutsumanimi'),
        blank=True)
    history = models.TextField(
        verbose_name=_(u'Viljelyhistoria'),
        help_text=_(
            u'Tietoja alkuperästä ja viljelyhistoriasta: '
            u'Kuinka kauan se on kasvanut nykyisellä paikallaan? '
            u'Mistä se on alun perin saatu? '
            u'Arviolta millä vuosikymmenellä sen tiedetään kasvaneen? '
            u'Kuka sitä on viljellyt?'),
        blank=True)
    stories = models.TextField(
        verbose_name=_(u'Tarinat'),
        help_text=_(u'Kasviin liittyvä tarina, tapahtuma'),
        blank=True)
    pictures = models.TextField(
        verbose_name=_(u'Kuvat'),
        blank=True)
    environment = models.TextField(
        verbose_name=_(u'Kasvuympäristö'),
        help_text=_(u'Maaperä ja kasvupaikka'),
        blank=True)

    def __unicode__(self):
        if self.variation:
            return u'%s/%s (%s)' % (self.name_fi(),
                                    self.variation,
                                    self.origin)
        return u'%s (%s)' % (self.name_fi(), self.origin)

    def name_fi(self):
        return self.species.name_fi
    name_fi.short_description = Species._meta.get_field('name_fi').verbose_name

    def genus(self):
        return self.species.genus
    genus.short_description = Species._meta.get_field('genus').verbose_name

    def species_species(self):
        return self.species.species
    species_species.short_description = Species._meta.get_field('species').verbose_name

    def subspecies(self):
        return self.species.subspecies
    subspecies.short_description = Species._meta.get_field('subspecies').verbose_name

    class Meta:
        verbose_name = _(u'observation')
        verbose_name_plural = _(u'observations')
        ordering = 'species__name_fi',


class Plot(models.Model):
    name = models.CharField(max_length=80,
                            verbose_name=_(u'name'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'garden plot')
        verbose_name_plural = _(u'garden plots')


class Bed(models.Model):
    plot = models.ForeignKey(
        Plot,
        null=True, blank=True,
        verbose_name=_(u'plot'))
    name = models.CharField(
        max_length=80,
        verbose_name=_(u'name'))
    description = models.TextField(
        blank=True,
        verbose_name=_(u'description'))

    def __unicode__(self):
        if self.plot:
            return u'%s/%s' % (self.plot, self.name)
        return self.name

    class Meta:
        verbose_name = _(u'bed')
        verbose_name_plural = _(u'beds')


class Planting(models.Model):
    observation = models.ForeignKey(
        Observation,
        verbose_name=_(u'observation'))
    bed = models.ForeignKey(
        Bed,
        verbose_name=_(u'bed'))
    planting_date = models.DateField(
        verbose_name=_(u'date of planting'))
    count = models.IntegerField(
        verbose_name=_(u'count'))
    removal_date = models.DateField(
        null=True, blank=True,
        verbose_name=_(u'date of removal'))

    def __unicode__(self):
        return unicode(self.observation)

    @property
    def last_care(self):
        try:
            return self.care_set.order_by('-date')[0]
        except IndexError:
            return None

    def last_care_date(self):
        try:
            return self.last_care.date
        except AttributeError:
            return u''
    last_care_date.short_description = _('date of last care operation')

    def last_care_description(self):
        try:
            return self.last_care.description
        except AttributeError:
            return u''
    last_care_description.short_description = _('last care operation')

    def last_care_count(self):
        try:
            return self.last_care.count
        except AttributeError:
            return u''
    last_care_count.short_description = _('count after care')

    class Meta:
        verbose_name = _(u'planting')
        verbose_name_plural = _(u'plantings')
        ordering = 'observation__species__name_fi',


class PlantingPhoto(models.Model):
    planting = models.ForeignKey(
        Planting,
        verbose_name=_(u'planting'))
    photo = models.ImageField(
        verbose_name=_(u'photo'),
        upload_to='photos/planting')
    date = models.DateField(
        verbose_name=_(u'date of photo'))
    photographer = models.CharField(
        max_length=80,
        verbose_name=_(u'name of photographer'))

    def __unicode__(self):
        return u'%s: %s' % (self.planting, self.observation)

    class Meta:
        verbose_name = _(u'planting')
        verbose_name_plural = _(u'plantings')


class Care(models.Model):
    planting = models.ForeignKey(
        Planting,
        verbose_name=_(u'planting'),
        help_text=_(u'Specify the planting'))
    date = models.DateField(
        verbose_name=_(u'date'))
    description = models.TextField(
        verbose_name=_(u'description'))
    count = models.IntegerField(
        verbose_name=_(u'number of plants after care'))

    def __unicode__(self):
        return u'%s: %s / %s' % (self.date, self.planting, self.description)

    class Meta:
        verbose_name = _(u'care')
        verbose_name_plural = _(u'care operations')
        ordering = 'date',
