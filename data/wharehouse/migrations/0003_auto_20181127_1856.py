# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-27 18:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    def create_objects(apps, schema_editor):
        """
        Copia todo o conteúdo da tabela log_exercicios para ExercicesDataWharehouse.
        """
        Tbl_log_exercicios = apps.get_model('app', 'ExercicioLog')
        Tbl_wharehouse = apps.get_model('wharehouse', 'ExercisesDataWharehouse')
        Turma = apps.get_model('app', 'Turma')
        Alternativa = apps.get_model('app', 'Alternativa')
        Resposta = apps.get_model('app', 'Resposta')
        bulk_data = []

        for log in Tbl_log_exercicios.objects.all():
            turma_aluno = Turma.objects.filter(alunos=log.aluno)
            alternativa_correta = Alternativa.objects.filter(
                exercicio=log.exercicio, correta=True)
            resposta_aluno = Resposta.objects.filter(
                exercicio=log.exercicio, aluno=log.aluno)

            if alternativa_correta.count() > 0 and resposta_aluno.count() > 0 and turma_aluno.count() > 0:
                bulk_data.append(
                    Tbl_wharehouse(
                        escola = log.aluno.escola,
                        turma = turma_aluno[0],
                        serie = log.exercicio.aula.serie,
                        bimestre = log.exercicio.aula.bimestre,
                        aluno = log.aluno,
                        exercicio = log.exercicio,
                        disciplina = log.exercicio.aula.disciplina,
                        is_prova_brasil = log.exercicio.aula.disciplina.is_prova_brasil,
                        resposta = resposta_aluno[0].alternativa,
                        gabarito = alternativa_correta[0]
                    )
                )
            else:
                print("Log de exercício sem resposta ou aluno sem turma")
        Tbl_wharehouse.objects.bulk_create(bulk_data)

    dependencies = [
        ('wharehouse', '0002_desempenhoturmawharehouse'),
    ]

    operations = [
        migrations.RunPython(create_objects),
    ]
