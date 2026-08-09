# -*- coding: utf-8 -*-
"""Widen ``Contact.email`` to 254 characters (upgrade plan Stage 6).

The field declares no ``max_length``, so it follows Django's default --
75 up to Django 1.7, 254 from 1.8, the RFC 3696 limit. The model did not
change; the default under it did.
"""
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kasvimuseo', '0002_photo_sizes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='S\xe4hk\xf6Posti', blank=True),
        ),
    ]
