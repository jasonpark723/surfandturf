# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-09-20 20:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surfsup', '0009_auto_20190920_0105'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='promo_valid',
            field=models.BooleanField(default=False),
        ),
    ]
