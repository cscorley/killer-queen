# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-13 01:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0008_auto_20171211_0112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='trueskill_rating_exposure',
            field=models.FloatField(default=0.0, verbose_name='TrueSkill.Rating exposure.  Use this for sorting'),
        ),
        migrations.AlterField(
            model_name='player',
            name='trueskill_rating_mu',
            field=models.FloatField(default=25.0, verbose_name='TrueSkill.Rating mu parameter'),
        ),
        migrations.AlterField(
            model_name='player',
            name='trueskill_rating_sigma',
            field=models.FloatField(default=8.333333333333334, verbose_name='TrueSkill.Rating sigma parameter'),
        ),
        migrations.AlterUniqueTogether(
            name='eventplayer',
            unique_together=set([('player', 'event')]),
        ),
        migrations.AlterUniqueTogether(
            name='eventteam',
            unique_together=set([('team', 'event')]),
        ),
        migrations.AlterUniqueTogether(
            name='teammembership',
            unique_together=set([('team', 'player')]),
        ),
    ]