# Generated by Django 2.1.5 on 2019-04-05 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0041_auto_20190316_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='cab_bracket',
            field=models.TextField(default='{}', verbose_name='Cab Bracket'),
        ),
    ]
