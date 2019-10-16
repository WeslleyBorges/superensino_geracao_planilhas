from django.test import TestCase
from model_mommy import mommy
from .models import ExercisesDataWharehouse
from app.models import Aluno, Disciplina, Exercicio, Professor, Turma, TurmaDisciplina, HistoricoAulasAssistidas
from superens.utils import answer_exercise_4_tests, ppdict, visualize_aula
from data.wharehouse import helpers

from django.db import models
from django.db.models import Q, F
import pprint
from core.tests import SuperEnsinoWithFixturesTestCase


class ExercisesDataWharehouseTestCase(TestCase):
    def setUp(self):

        self.escola = mommy.make('app.Escola')
        self.turma = mommy.make('app.Turma')
        self.aluno = mommy.make('app.Aluno', escola=self.escola)

        # Adiciona o aluno a turma
        self.turma.alunos.add(self.aluno)
        self.turma.save()

        self.exercicio = mommy.make('app.Exercicio')

        self.alternativas = mommy.make(
            'app.Alternativa',
            _quantity=4,
            exercicio=self.exercicio,
            correta=False)

        # define a alternativa 1 como a correta
        self.alternativas[0].correta = True
        self.alternativas[0].save()

    def tearDown(self):
        self.escola.delete()
        self.turma.delete()
        self.aluno.delete()
        self.exercicio.delete()


    def test_add_method(self):
        data = ExercisesDataWharehouse.add(self.aluno, self.exercicio, self.alternativas[0])

        self.assertEqual(data.escola, self.escola)
        self.assertEqual(data.turma, self.aluno.turma_atual())
        self.assertEqual(data.serie, self.exercicio.aula.serie)
        self.assertEqual(data.bimestre, self.exercicio.aula.bimestre)
        self.assertEqual(data.aluno, self.aluno)
        self.assertEqual(data.exercicio, self.exercicio)
        self.assertEqual(data.disciplina, self.exercicio.aula.disciplina)
        self.assertEqual(data.is_prova_brasil, self.exercicio.aula.disciplina.is_prova_brasil)
        self.assertEqual(data.resposta, self.alternativas[0])
        self.assertEqual(data.gabarito, self.exercicio.alternativa_correta())


class ExerciciosDataWharehouseQuerySetTestCase(SuperEnsinoWithFixturesTestCase):

    def test_get_desempenho_turma(self):
        rs= ExercisesDataWharehouse.objects.get_desempenho_turmas_professor(
            self.prof_rose, self._5anoA_SuperEnsino.escola)

        self.assertEqual('Escola Super Ensino', rs[0]['escola__nome'])
        self.assertEqual('História', rs[0]['disciplina__nome'])
        self.assertEqual(4, rs[0]['correta'])
        self.assertEqual(20, rs[0]['exercicios_realizados'])

        self.assertEqual('Escola Super Ensino', rs[1]['escola__nome'])
        self.assertEqual('Geografia', rs[1]['disciplina__nome'])
        self.assertEqual(10, rs[1]['correta'])
        self.assertEqual(20, rs[1]['exercicios_realizados'])

    def test_get_max_and_min_turma(self):
        daniel = Aluno.objects.get(nome='Daniel')
        maria = Aluno.objects.get(nome='Maria')

        answer_exercise_4_tests(daniel, self.matematica, 10, 7)
        answer_exercise_4_tests(daniel, self.historia, 10, 5)
        answer_exercise_4_tests(daniel, self.geografia, 10, 5)

        answer_exercise_4_tests(maria, self.matematica, 10, 3)
        answer_exercise_4_tests(maria, self.historia, 10, 3)
        answer_exercise_4_tests(maria, self.geografia, 10, 3)

        _5anoA_SuperEnsino = Turma.objects.get(pk=1)

        minIndice = ExercisesDataWharehouse.objects.get_pior_desempenho_disciplina_turma(self.geografia, _5anoA_SuperEnsino)
        self.assertEqual(minIndice, 50)

        maxIndice = ExercisesDataWharehouse.objects.get_melhor_desempenho_disciplina_turma(self.geografia, _5anoA_SuperEnsino)
        self.assertEqual(maxIndice, 70)

    def test_get_desempenho_turma_disciplina_details(self):
        daniel = Aluno.objects.get(nome='Daniel')
        maria = Aluno.objects.get(nome='Maria')
        answer_exercise_4_tests(daniel, self.historia, 10, 5)
        answer_exercise_4_tests(maria, self.historia, 10, 3)

        result = ExercisesDataWharehouse.objects.get_desempenho_turma_disciplina_details(
            self._5anoA_SuperEnsino, self.historia)
        print(result)
