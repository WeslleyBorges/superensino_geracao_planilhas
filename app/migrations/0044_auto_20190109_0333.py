# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-01-09 03:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_turma_turno'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turma',
            name='turno',
            field=models.CharField(choices=[('MAT', 'MAT'), ('VESP', 'VESP')], default='MAT', max_length=15),
        ),
    ]