# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-07-26 21:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0053_auto_20190723_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professor',
            name='escola',
            field=models.ManyToManyField(blank=True, to='app.Escola'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='genero',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Masculino'), (2, 'Feminino')], default=1, null=True),
        ),
    ]
