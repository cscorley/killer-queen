# Generated by Django 2.1.5 on 2019-03-17 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0038_cabinformation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cabinformation',
            name='id',
        ),
        migrations.AlterField(
            model_name='cabinformation',
            name='name',
            field=models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='name'),
        ),
    ]
