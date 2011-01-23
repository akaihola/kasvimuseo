# -*- coding: utf-8 -*-

from django.db import models
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


class Species(models.Model):
    external_id = models.IntegerField(
        verbose_name=_(u'LajiNro'),
        null=True, blank=True)
    type = models.IntegerField(
        choices=PLANT_TYPE_CHOICES)
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
        verbose_name=_(u'AlalajiMuoto'),
        blank=True)
    variety = models.CharField(
        max_length=40,
        verbose_name=_(u'lajike'),
        blank=True)
    name_fi = models.CharField(
        max_length=40,
        verbose_name=_(u'SuomalainenNimi'))
    name_sv = models.CharField(
        max_length=40,
        verbose_name=_(u'RuotsinkielinenNimi'),
        blank=True)
    name_local = models.CharField(
        max_length=40,
        verbose_name=_(u'PaikallinenNimi'),
        blank=True)
    abbr_fi = models.CharField(
        max_length=20,
        verbose_name=_(u'Lyhenne_suomalainen'),
        blank=True)
    abbr_scientific = models.CharField(
        max_length=20,
        verbose_name=_(u'Lyhenne_tieteellinen'),
        blank=True)
    height = models.CharField(
        max_length=40,
        verbose_name=_(u'korkeuscm'),
        blank=True)
    width = models.CharField(
        max_length=40,
        verbose_name=_(u'leveyscm'),
        blank=True)
    flower_color = models.CharField(
        max_length=40,
        verbose_name=_(u'kukinnanväri'),
        blank=True)
    flowering_time = models.CharField(
        max_length=20,
        verbose_name=_(u'kukintaAika'),
        blank=True)
    substrate = models.TextField(
        verbose_name=_(u'Kasvualusta'),
        blank=True)
    spacing = models.TextField(
        verbose_name=_(u'Taimiväli'),
        blank=True)

    def __unicode__(self):
        return self.name_fi

    class Meta:
        verbose_name = _(u'(one) species')
        verbose_name_plural = _(u'(all) species')


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


class LocationContact(models.Model):
    location = models.ForeignKey(Location)
    contact = models.ForeignKey(Contact)

    def __unicode__(self):
        return u'%s/%s' % (self.location, self.contact)

    class Meta:
        verbose_name = _(u'contact for location')
        verbose_name_plural = _(u'contacts for locations')
        db_table = 'kasvimuseo_location_contacts'  # default for ManyToMany


class Observation(models.Model):
    external_id = models.IntegerField(
        null=True, blank=True,
        verbose_name=_(u'YläneNro'))
    origin = models.ForeignKey(
        Location,
        verbose_name=_(u'Kasvin alkuperä'))
    species = models.ForeignKey(
        Species,
        verbose_name=_(u'Kasvilaji'))
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
        return u'%s (%s %s)' % (self.species, self.origin, self.date)

    class Meta:
        verbose_name = _(u'observation')
        verbose_name_plural = _(u'observations')


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
        return u'%s: %s' % (self.planting_date, self.observation)

    class Meta:
        verbose_name = _(u'planting')
        verbose_name_plural = _(u'plantings')


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
