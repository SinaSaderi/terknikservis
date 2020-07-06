# Generated by Django 3.0.8 on 2020-07-06 15:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_auto_20200706_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='created_at',
            field=models.DateField(default=datetime.date.today, verbose_name='Created at'),
        ),
        migrations.AddField(
            model_name='service',
            name='register_date',
            field=models.DateField(blank=True, null=True, verbose_name='Register date'),
        ),
    ]