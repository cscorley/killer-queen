# Generated by Django 2.0 on 2017-12-20 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0016_randomname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='randomname',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='name'),
        ),
    ]
