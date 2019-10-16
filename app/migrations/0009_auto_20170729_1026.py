# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-29 14:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_exerciciolog'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aula',
            options={'ordering': ['assunto']},
        ),
        migrations.AlterModelOptions(
            name='exercicio',
            options={'ordering': ['aula__assunto']},
        ),
        migrations.AddField(
            model_name='resposta',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
