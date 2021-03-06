# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-09-20 01:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surfsup', '0008_searchmanager'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('discount', models.FloatField()),
                ('description', models.TextField()),
                ('expiration_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='SearchManager',
        ),
    ]
