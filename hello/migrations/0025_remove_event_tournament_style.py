# Generated by Django 2.0.1 on 2018-04-05 04:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0024_event_tournament_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='tournament_style',
        ),
    ]
