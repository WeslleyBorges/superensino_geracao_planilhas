# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-15 18:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0040_auto_20181109_1953'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExercisesDataWharehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serie', models.IntegerField()),
                ('bimestre', models.IntegerField()),
                ('is_prova_brasil', models.BooleanField()),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Aluno')),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Disciplina')),
                ('escola', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Escola')),
                ('exercicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Exercicio')),
                ('gabarito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gabarito', to='app.Alternativa')),
                ('resposta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respaluno', to='app.Alternativa')),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Turma')),
            ],
        ),
    ]