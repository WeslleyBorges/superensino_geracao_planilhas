# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-07-27 04:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_aluno_escola'),
    ]

    operations = [
        migrations.AddField(
            model_name='responsavel',
            name='escola',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Escola'),
        ),
    ]
