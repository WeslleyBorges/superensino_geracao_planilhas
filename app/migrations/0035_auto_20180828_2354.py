# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-08-28 23:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_auto_20180824_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='escola',
            name='slug',
            field=models.SlugField(blank=True, default=None, null=True, unique=True),
        ),
    ]
