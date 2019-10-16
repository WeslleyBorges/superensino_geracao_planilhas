# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 14:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_historicoaulasassistidas'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExercicioLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Aluno')),
                ('exercicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Exercicio')),
            ],
        ),
    ]
