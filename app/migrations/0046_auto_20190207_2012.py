# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-02-07 20:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0045_turma_letra'),
    ]

    operations = [
        migrations.AddField(
            model_name='escola',
            name='primeiro_bimestre_ativo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='escola',
            name='quarto_bimestre_ativo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='escola',
            name='segundo_bimestre_ativo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='escola',
            name='terceiro_bimestre_ativo',
            field=models.BooleanField(default=False),
        ),
    ]
