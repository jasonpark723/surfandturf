# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-09-16 20:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surfsup', '0004_auto_20190916_0222'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='items',
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(blank=True, null=True, related_name='orders', to='surfsup.OrderItem'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='surfsup.User'),
        ),
    ]
