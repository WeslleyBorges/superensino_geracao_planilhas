# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-19 20:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0040_auto_20181109_1953'),
        ('wharehouse', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DesempenhoTurmaWharehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menorDesempenho', models.IntegerField()),
                ('maiorDesempenho', models.IntegerField()),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Turma')),
            ],
        ),
    ]
