# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-09 19:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_endereco_uf'),
    ]

    operations = [
        migrations.CreateModel(
            name='TurmaDisciplina',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Disciplina')),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grade_curricular', to='app.Professor')),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vinculo', to='app.Turma')),
            ],
        ),
        migrations.AlterField(
            model_name='endereco',
            name='uf',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='UF'),
        ),
        migrations.AddField(
            model_name='professor',
            name='classes',
            field=models.ManyToManyField(related_name='turmas', through='app.TurmaDisciplina', to='app.Turma'),
        ),
    ]
