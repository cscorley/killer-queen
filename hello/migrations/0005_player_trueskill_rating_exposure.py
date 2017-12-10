# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-10 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0004_auto_20171210_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='trueskill_rating_exposure',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10, verbose_name='TrueSkill.Rating exposure.  Use this for sorting'),
            preserve_default=False,
        ),
    ]
