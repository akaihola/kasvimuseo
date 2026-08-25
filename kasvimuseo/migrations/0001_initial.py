# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('public', models.BooleanField(default=False, verbose_name='public')),
            ],
            options={
                'verbose_name': 'bed',
                'verbose_name_plural': 'beds',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Care',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='date')),
                ('description', models.TextField(verbose_name='description')),
                ('count', models.IntegerField(verbose_name='number of plants after care')),
            ],
            options={
                'ordering': ('date',),
                'verbose_name': 'care',
                'verbose_name_plural': 'care operations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_name', models.CharField(max_length=40, verbose_name='SukuNimi')),
                ('first_name', models.CharField(max_length=40, verbose_name='EtuNimi')),
                ('phone', models.CharField(max_length=40, verbose_name='LankaPuh', blank=True)),
                ('mobile', models.CharField(max_length=40, verbose_name='MatkaPuh', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='S\xe4hk\xf6Posti', blank=True)),
                ('street', models.CharField(max_length=80, verbose_name='KatuOsoite', blank=True)),
                ('number', models.CharField(max_length=20, verbose_name='N:o', blank=True)),
                ('apartment', models.CharField(max_length=20, verbose_name='as', blank=True)),
                ('zipcode', models.CharField(max_length=5, verbose_name='PostiNro', blank=True)),
                ('city', models.CharField(max_length=40, verbose_name='PostiToimiPaikka', blank=True)),
                ('description', models.TextField(verbose_name='Lis\xe4tieto', blank=True)),
            ],
            options={
                'ordering': ('last_name',),
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visible', models.BooleanField(default=True)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='photologue.Photo', null=True)),
            ],
            options={
                'verbose_name': 'label',
                'verbose_name_plural': 'labels',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('external_id', models.IntegerField(null=True, verbose_name='YhteysNro', blank=True)),
                ('name', models.CharField(max_length=40, verbose_name='Talo')),
                ('alias', models.CharField(max_length=40, verbose_name='Toinen nimitys', blank=True)),
                ('village', models.CharField(max_length=40, verbose_name='Kyl\xe4', blank=True)),
                ('area', models.CharField(max_length=40, verbose_name='Asuinalue', blank=True)),
                ('street', models.CharField(max_length=80, verbose_name='KatuOsoite', blank=True)),
                ('number', models.CharField(max_length=20, verbose_name='N:o', blank=True)),
                ('apartment', models.CharField(max_length=20, verbose_name='as', blank=True)),
                ('zipcode', models.CharField(max_length=5, verbose_name='PostiNro', blank=True)),
                ('city', models.CharField(max_length=40, verbose_name='PostiToimiPaikka', blank=True)),
                ('history', models.TextField(help_text='Tietoja talon ja puutarhan historiasta', verbose_name='Historia', blank=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'location',
                'verbose_name_plural': 'locations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kasvimuseo.Contact')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kasvimuseo.Location')),
            ],
            options={
                'db_table': 'kasvimuseo_location_contacts',
                'verbose_name': 'contact for location',
                'verbose_name_plural': 'contacts for locations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('external_id', models.IntegerField(null=True, verbose_name='Yl\xe4neNro', blank=True)),
                ('variation', models.CharField(max_length=200, verbose_name='color/form', blank=True)),
                ('date', models.DateField(verbose_name='Havaintop\xe4iv\xe4')),
                ('characteristics', models.TextField(help_text='Milt\xe4 se n\xe4ytt\xe4\xe4?', verbose_name='Tuntomerkkej\xe4', blank=True)),
                ('nickname', models.CharField(max_length=200, verbose_name='Kutsumanimi', blank=True)),
                ('history', models.TextField(help_text='Tietoja alkuper\xe4st\xe4 ja viljelyhistoriasta: Kuinka kauan se on kasvanut nykyisell\xe4 paikallaan? Mist\xe4 se on alun perin saatu? Arviolta mill\xe4 vuosikymmenell\xe4 sen tiedet\xe4\xe4n kasvaneen? Kuka sit\xe4 on viljellyt?', verbose_name='Viljelyhistoria', blank=True)),
                ('stories', models.TextField(help_text='Kasviin liittyv\xe4 tarina, tapahtuma', verbose_name='Tarinat', blank=True)),
                ('pictures', models.TextField(verbose_name='Kuvat', blank=True)),
                ('notes', models.TextField(verbose_name='notes', blank=True)),
                ('environment', models.TextField(help_text='Maaper\xe4 ja kasvupaikka', verbose_name='Kasvuymp\xe4rist\xf6', blank=True)),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, verbose_name='Kasvin alkuper\xe4', to='kasvimuseo.Location')),
            ],
            options={
                'ordering': ('species__name_fi',),
                'verbose_name': 'observation',
                'verbose_name_plural': 'observations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Planting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('planting_date', models.DateField(verbose_name='date of planting')),
                ('count', models.IntegerField(verbose_name='count')),
                ('distance_left', models.IntegerField(default=15, help_text='distance in cm from the left edge of the bed', verbose_name='distance left')),
                ('distance_front', models.IntegerField(default=15, help_text='distance in cm from the front edge of the bed', verbose_name='distance front')),
                ('width', models.IntegerField(default=15, help_text='width of the planting in cm', verbose_name='width')),
                ('depth', models.IntegerField(default=15, help_text='depth of the planting in cm', verbose_name='depth')),
                ('removal_date', models.DateField(null=True, verbose_name='date of removal', blank=True)),
                ('bed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, verbose_name='bed', to='kasvimuseo.Bed')),
                ('label', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='label', blank=True, to='kasvimuseo.Label', null=True)),
                ('observation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, verbose_name='observation', to='kasvimuseo.Observation')),
            ],
            options={
                'ordering': ('observation__species__name_fi',),
                'verbose_name': 'planting',
                'verbose_name_plural': 'plantings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlantingPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('photo', models.ImageField(upload_to='photos/planting', verbose_name='photo')),
                ('date', models.DateField(verbose_name='date of photo')),
                ('photographer', models.CharField(max_length=80, verbose_name='name of photographer')),
                ('planting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, verbose_name='planting', to='kasvimuseo.Planting')),
            ],
            options={
                'verbose_name': 'planting',
                'verbose_name_plural': 'plantings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Plot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='name')),
            ],
            options={
                'verbose_name': 'garden plot',
                'verbose_name_plural': 'garden plots',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('external_id', models.IntegerField(null=True, verbose_name='LajiNro', blank=True)),
                ('type', models.IntegerField(verbose_name='type', choices=[(1, 'Yksi/kaksiv. koristekasvi'), (2, 'Perenna'), (3, 'Yrtti'), (4, 'Muu hy\xf6tykasvi'), (5, 'Koristepensas'), (6, 'Koristek\xf6ynn\xf6s'), (7, 'Marja'), (8, 'Marjapensas'), (9, 'Koristepuu'), (10, 'Hedelm\xe4puu'), (11, 'Luonnonkasvi')])),
                ('genus', models.CharField(max_length=40, verbose_name='Sukunimi')),
                ('group', models.CharField(max_length=40, verbose_name='Ryhm\xe4', blank=True)),
                ('species', models.CharField(max_length=40, verbose_name='Laji')),
                ('subspecies', models.CharField(max_length=40, verbose_name='subspecies', blank=True)),
                ('variety', models.CharField(max_length=40, verbose_name='lajike', blank=True)),
                ('cultivation_history', models.TextField(verbose_name='cultivation history', blank=True)),
                ('name_fi', models.CharField(max_length=40, verbose_name='SuomalainenNimi')),
                ('height', models.CharField(max_length=40, verbose_name='korkeuscm', blank=True)),
                ('width', models.CharField(max_length=40, verbose_name='leveyscm', blank=True)),
                ('spacing', models.TextField(verbose_name='Taimiv\xe4li', blank=True)),
                ('flower_color', models.CharField(max_length=80, verbose_name='kukinnanv\xe4ri', blank=True)),
                ('flowering_start', models.IntegerField(blank=True, null=True, verbose_name='first flowering month', choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
                ('flowering_end', models.IntegerField(blank=True, null=True, verbose_name='last flowering month', choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
                ('lighting', models.IntegerField(blank=True, null=True, verbose_name='light requirement', choices=[(1, 'A'), (2, 'A-Pv'), (3, 'Pv'), (4, 'Pv-V'), (5, 'V'), (6, 'A-V')])),
                ('substrate', models.TextField(verbose_name='Kasvualusta', blank=True)),
                ('additional_info', models.TextField(verbose_name='additional information', blank=True)),
                ('photo_is_horizontal', models.NullBooleanField(default=None, verbose_name='photo is wider than it is tall', editable=False)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='photologue.Photo', null=True)),
            ],
            options={
                'ordering': ('name_fi',),
                'verbose_name': '(one) species',
                'verbose_name_plural': '(all) species',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='observation',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, verbose_name='Kasvilaji', to='kasvimuseo.Species'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='locationcontact',
            unique_together=set([('location', 'contact')]),
        ),
        migrations.AddField(
            model_name='location',
            name='contacts',
            field=models.ManyToManyField(to='kasvimuseo.Contact', through='kasvimuseo.LocationContact'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='label',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, verbose_name='species', to='kasvimuseo.Species'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='care',
            name='planting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, verbose_name='planting', to='kasvimuseo.Planting', help_text='Specify the planting'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bed',
            name='plot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='plot', blank=True, to='kasvimuseo.Plot', null=True),
            preserve_default=True,
        ),
    ]
