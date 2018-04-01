# Generated by Django 2.0.1 on 2018-04-01 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0022_auto_20180327_0231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='season',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='hello.Season'),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=255, verbose_name='name'),
        ),
    ]
