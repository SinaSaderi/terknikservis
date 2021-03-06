# Generated by Django 3.0.8 on 2020-07-06 13:20

import apps.service.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('status', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Serial number')),
                ('register_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Register number')),
                ('model', models.CharField(blank=True, max_length=255, null=True, verbose_name='Model/Color')),
                ('capacity', models.CharField(blank=True, max_length=255, null=True, verbose_name='Capacity')),
                ('imei_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Imei number')),
                ('warranty', models.BooleanField(blank=True, default=0, null=True, verbose_name='Warranty')),
                ('delivery_date', models.DateField(blank=True, null=True, verbose_name='Delivery date')),
                ('init_comment', models.TextField(blank=True, null=True, verbose_name='Initial comment')),
                ('problem', models.TextField(blank=True, null=True, verbose_name='Problem')),
                ('product', models.ForeignKey(on_delete=models.SET(apps.service.models.safe_remove), related_name='product', to='product.Product', verbose_name='Product')),
                ('status', models.ForeignKey(on_delete=models.SET(apps.service.models.safe_remove), related_name='status', to='status.Status', verbose_name='Status')),
                ('user', models.ForeignKey(on_delete=models.SET(apps.service.models.safe_remove), related_name='customer', to=settings.AUTH_USER_MODEL, verbose_name='Customer')),
            ],
            options={
                'verbose_name': 'Service',
                'verbose_name_plural': 'Services',
            },
        ),
        migrations.CreateModel(
            name='Piece',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('amount', models.FloatField(default=0, verbose_name='Service amount')),
                ('service', models.ForeignKey(on_delete=models.SET(apps.service.models.safe_remove), related_name='service_pieces', to='service.Service', verbose_name='Service')),
            ],
            options={
                'verbose_name': 'Piece',
                'verbose_name_plural': 'Pieces',
            },
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('price', models.FloatField(default=0, verbose_name='Price')),
                ('service', models.ForeignKey(on_delete=models.SET(apps.service.models.safe_remove), related_name='service_operation', to='service.Service', verbose_name='Service')),
            ],
            options={
                'verbose_name': 'Operation',
                'verbose_name_plural': 'Operations',
            },
        ),
    ]
