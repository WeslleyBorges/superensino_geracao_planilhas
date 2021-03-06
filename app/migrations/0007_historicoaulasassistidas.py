# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 05:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20170723_1556'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoAulasAssistidas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Aluno')),
                ('aula', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Aula')),
            ],
        ),
    ]
