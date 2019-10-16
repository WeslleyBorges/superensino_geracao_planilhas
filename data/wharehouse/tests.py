from django.test import TestCase
from model_mommy import mommy
from .models import ExercisesDataWharehouse
from app.models import Aluno, Disciplina, Exercicio, Professor, Turma, TurmaDisciplina
from data.wharehouse import helpers

# Create your tests here.
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


class ExerciciosDataWharehouseQuerySetTestCase(TestCase):
    fixtures = ['db.json']

    def answer_exercises(self, aluno, disciplina, quantity, corretas):
        index = 0
        exercicios = Exercicio.objects.filter(
            aula__disciplina=disciplina)[:quantity]

        for e in exercicios:
            if index < corretas:
                ExercisesDataWharehouse.add(aluno, e, e.get_alternativa(1))
            else:
                ExercisesDataWharehouse.add(aluno, e, e.get_alternativa(0))

            index+=1

    def setUp(self):
        self.pedro = Aluno.objects.get(nome='Pedro')
        self.harry = Aluno.objects.get(nome='HARRY POTTER')

        self.matematica = Disciplina.objects.get(nome='Matemática', is_prova_brasil=False)
        self.historia = Disciplina.objects.get(nome='História')
        self.geografia = Disciplina.objects.get(nome='Geografia')

        self.answer_exercises(self.pedro, self.matematica, 10, 2)
        self.answer_exercises(self.pedro, self.historia, 10, 8)
        self.answer_exercises(self.pedro, self.geografia, 10, 5)

        self.answer_exercises(self.harry, self.matematica, 10, 2)
        self.answer_exercises(self.harry, self.historia, 10, 8)
        self.answer_exercises(self.harry, self.geografia, 10, 5)

        # 1. Setup de professores da Super ensino
        self.prof_rose = Professor.objects.get(nome='Rose')
        _5anoA_SuperEnsino = Turma.objects.get(pk=1)
        _5anoA_Hogwarts = Turma.objects.get(pk=4)

        # 1.1 Configuração de turmas da Prof. Rose
        TurmaDisciplina.objects.create(
            professor=self.prof_rose, turma=_5anoA_SuperEnsino, disciplina=self.historia)

        TurmaDisciplina.objects.create(
            professor=self.prof_rose, turma=_5anoA_SuperEnsino, disciplina=self.geografia)

        TurmaDisciplina.objects.create(
            professor=self.prof_rose, turma=_5anoA_Hogwarts, disciplina=self.geografia)


    def tearDown(self):
        ExercisesDataWharehouse.objects.all().delete()
        TurmaDisciplina.objects.all().delete()

    def test_get_desempenho_turma(self):
        rs= ExercisesDataWharehouse.objects.get_desempenho_turmas_professor(self.prof_rose)
        self.assertEqual('Escola Super Ensino', rs[0]['escola__nome'])
        self.assertEqual('Geografia', rs[0]['disciplina__nome'])
        self.assertEqual(10, rs[0]['correta'])
        self.assertEqual(20, rs[0]['exercicios_realizados'])

        self.assertEqual('Escola Super Ensino', rs[1]['escola__nome'])
        self.assertEqual('História', rs[1]['disciplina__nome'])
        self.assertEqual(4, rs[1]['correta'])
        self.assertEqual(20, rs[1]['exercicios_realizados'])

        self.assertEqual('Hogwarts', rs[2]['escola__nome'])
        self.assertEqual('Geografia', rs[2]['disciplina__nome'])
        self.assertEqual(5, rs[2]['correta'])
        self.assertEqual(10, rs[2]['exercicios_realizados'])

        self.assertEqual('Hogwarts', rs[3]['escola__nome'])
        self.assertEqual('História', rs[3]['disciplina__nome'])
        self.assertEqual(2, rs[3]['correta'])
        self.assertEqual(10, rs[3]['exercicios_realizados'])


class HelpersTestCase(TestCase, SuperEnsinoWithFixturesTestCase):
    """Suite de teste para os métodos Helpers do Wharehouse."""

    def test_query_consulta_desempenho_alunos_turma(self):
        helpers.query_consulta_desempenho_alunos_turma()
