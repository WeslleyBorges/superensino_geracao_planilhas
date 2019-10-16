from app.queries import get_desempenho_por_serie
from app import queries
from core.tests import SuperEnsinoTestCase
from model_mommy import mommy
from app.models import Aluno, Aula, HistoricoAulasAssistidas, Disciplina
from app.models import Exercicio
from app.models import Resposta
from app.models import Turma
from app.models import Escola
from app.models import Alternativa
from django.contrib.auth import get_user_model
from django.test import TestCase
from app import vimeo


class DesempenhoGeralProvaBrasilTestCase(SuperEnsinoTestCase):

    def test_100_aproveitamento_5_e_9_ano(self):
        self.resolve_exercicios(5)
        self.resolve_exercicios(9)

        result = desempenho_prova_brasil_por_series()
        self.assertEqual(result[0]['corretas'], 4400, 'Validação 5ano')
        self.assertEqual(result[0]['erradas'], 0, 'Validação 5ano')
        self.assertEqual(result[0]['aproveitamento'], 100, 'Validação 5ano')

        self.assertEqual(result[1]['corretas'], 3800, 'Validação 9ano')
        self.assertEqual(result[1]['erradas'], 0, 'Validação 9ano')
        self.assertEqual(result[1]['aproveitamento'], 100, 'Validação 9ano')

    def test_70_aproveitamento_5_e_9_ano(self):
        self.resolve_exercicios(5, 70)
        self.resolve_exercicios(9, 70)

        result = desempenho_prova_brasil_por_series()
        self.assertEqual(result[0]['corretas'], 3080, 'Validação 5ano')
        self.assertEqual(result[0]['erradas'], 1320, 'Validação 5ano')
        self.assertEqual(result[0]['aproveitamento'], 70, 'Validação 5ano')

        self.assertEqual(result[1]['corretas'], 2660, 'Validação 9ano')
        self.assertEqual(result[1]['erradas'], 1140, 'Validação 9ano')
        self.assertEqual(result[1]['aproveitamento'], 70, 'Validação 9ano')

    def test_respostas_5_ano(self):
        self.resolve_exercicios(5, 100, True)
        self.resolve_exercicios(5, 100, False)
        self.resolve_exercicios(6, 100, False)

        result = desempenho_prova_brasil_por_series()
        self.assertEqual(result[0]['corretas'], 4400, 'Validação 5ano')
        self.assertEqual(result[0]['erradas'], 0, 'Validação 5ano')
        self.assertEqual(result[0]['aproveitamento'], 100, 'Validação 5ano')

    def test_desempenho_serie_disciplina_por_assunto(self):
        self.resolve_exercicios(5, 70, False)
        disciplina = Disciplina.objects.get(nome='Portugues')
        queries.desempenho_serie_disciplina_por_assunto(
            self.escola, 5, disciplina)


class DesempenhoGeralSuperEnsinoTestCase(SuperEnsinoTestCase):
    def setUp(self):
        super(DesempenhoGeralSuperEnsinoTestCase, self).setUp()
        # Cria um aluno User para os tests do super aluno
        aluno_user = mommy.prepare(get_user_model())
        aluno_user.set_password('123456')
        aluno_user.save()

        self.aluno = Aluno.objects.first()
        self.aluno.user = aluno_user
        self.aluno.save()

    def test_100_aproveitamento_5_e_6_ano(self):
        self.resolve_exercicios(5, 100, False)
        self.resolve_exercicios(6, 100, False)

        total_ex_5_ano = self.calculate_max_responses_per_serie(5, False)
        total_ex_6_ano = self.calculate_max_responses_per_serie(6, False)

        result = desempenho_super_reforco_por_series()

        self.assertEqual(
            result[0]['corretas'], total_ex_5_ano, 'Validação 5ano')
        self.assertEqual(result[0]['erradas'], 0, 'Validação 5ano')
        self.assertEqual(result[0]['aproveitamento'], 100, 'Validação 5ano')

        self.assertEqual(
            result[1]['corretas'], total_ex_6_ano, 'Validação 6o ano')
        self.assertEqual(result[1]['erradas'], 0, 'Validação 6o ano')
        self.assertEqual(result[1]['aproveitamento'], 100, 'Validação 6o ano')

    def test_60_aproveitamento_5_e_6_ano(self):
        performance = 60
        self.resolve_exercicios(5, performance, False)
        self.resolve_exercicios(6, performance, False)

        total_ex_5_ano = self.calculate_max_responses_per_serie(5, False)
        total_ex_6_ano = self.calculate_max_responses_per_serie(6, False)

        result = desempenho_super_reforco_por_series()

        self.assertEqual(
            result[0]['corretas'],
            total_ex_5_ano * (performance/100), 'Validação 5ano')
        self.assertEqual(
            result[0]['erradas'],
            total_ex_5_ano - (total_ex_5_ano * performance/100),
            'Validação 5ano')
        self.assertEqual(
            result[0]['aproveitamento'], performance, 'Validação 5ano')

        self.assertEqual(
            result[1]['corretas'],
            total_ex_6_ano * (performance/100), 'Validação 6o ano')
        self.assertEqual(
            result[1]['erradas'],
            total_ex_6_ano - (total_ex_6_ano * performance/100),
            'Validação 6o ano')
        self.assertEqual(
            result[1]['aproveitamento'], performance, 'Validação 6o ano')

    def test_hist_aulas_assitidas_count(self):
        serie = 5
        aproveitamento = 70
        bimestre = 1
        self.resolve_exercicio_assunto(serie, aproveitamento, False)
        print(Aula.objects.filter(
                serie=5, disciplina=self.disc_portugues_se,
                disciplina__is_prova_brasil=False,
                bimestre=bimestre).count())
        # assiste uma video aula de cada assunto
        for aula in Aula.objects.filter(
                serie=5, disciplina__is_prova_brasil=False, bimestre=bimestre):
            attachment = aula.attachments.first()
            HistoricoAulasAssistidas.register_viewing(
                aula=aula, attachment=attachment, aluno=self.aluno)

        aa = HistoricoAulasAssistidas.objects.is_prova_brasil(
            False).serie(serie).bimestre(bimestre).disciplina(
            self.disc_portugues_se.id).count()

        self.assertEqual(aa, 10)

    def test_hist_aulas_assitidas_count2(self):
        turma = Turma.objects.get(identificador='5A')
        serie = 5
        aproveitamento = 70
        bimestre = 1
        self.resolve_exercicio_assunto(serie, aproveitamento, False)

        # assiste uma video aula de cada assunto
        for aula in Aula.objects.filter(
                serie=5, disciplina__is_prova_brasil=False, bimestre=bimestre):
            attachment = aula.attachments.first()
            HistoricoAulasAssistidas.register_viewing(
                aula=aula, attachment=attachment, aluno=self.aluno)

        aa = HistoricoAulasAssistidas.objects.is_prova_brasil(
            False).turma(turma.id).count()

        self.assertEqual(aa, 30)

    def test_visualizadores_unicos_turma(self):
        # assiste todas as aulas da serie bimestre
        for aula in Aula.objects.filter(
                serie=5, disciplina__is_prova_brasil=False, bimestre=1):
            for a in aula.attachments.all():
                HistoricoAulasAssistidas.register_viewing(
                    aula=aula, attachment=a, aluno=self.aluno)

        turma = Turma.objects.get(identificador='5A')
        unique_viewers = HistoricoAulasAssistidas.objects.turma(
            turma.id).distinct('aluno').count()

        self.assertEqual(unique_viewers, 1)


class RelatoriosTest(TestCase):
    def responde_exercicio(self, aluno, exercicio, opcao):
        alternativa = exercicio.alternativas.all()[opcao]
        Resposta.aplicar_resposta(aluno, exercicio, alternativa)

    def setUp(self):
        self.escola = mommy.make('app.Escola')

        self.alunos = mommy.make('app.Aluno', _quantity=10)

        self.turma = mommy.make(
            'app.Turma', escola=self.escola, serie=5, status=1)
        self.turma.alunos.add(*self.alunos)
        self.turma.save()

        self.portugues = mommy.make('app.Disciplina', nome='portugues')
        matematica = mommy.make('app.Disciplina', nome='matematica')

        self.digrafos = mommy.make(
            'app.Aula', serie=5,
            assunto='digrafos', disciplina=self.portugues)
        self.silabas = mommy.make(
            'app.Aula', serie=5,
            assunto='silabas', disciplina=self.portugues)
        self.nrprimos = mommy.make(
            'app.Aula', serie=5,
            assunto='nrprimos', disciplina=matematica)
        self.regradetres = mommy.make(
            'app.Aula', serie=5,
            assunto='regradetres', disciplina=matematica)

        assuntos = [
            self.digrafos, self.silabas, self.nrprimos, self.regradetres]

        for a in assuntos:
            exercicios = mommy.make('app.Exercicio', _quantity=5, aula=a)
            for e in exercicios:
                alternativas = mommy.make(
                    'app.Alternativa', _quantity=4, exercicio=e, correta=False)
                alternativas[0].correta = True
                alternativas[0].save()

        self.exercicio_digrafos = Exercicio.objects.filter(aula=self.digrafos)
        self.exercicio_silabas = Exercicio.objects.filter(aula=self.silabas)
        self.exercicio_nrprimos = Exercicio.objects.filter(aula=self.nrprimos)
        self.exercicio_regradetres = Exercicio.objects.filter(
            aula=self.regradetres)

    def tearDown(self):
        get_user_model().objects.all().delete()
        Exercicio.objects.all().delete()
        Turma.objects.all().delete()

    def test_sss(self):
        aluno = self.alunos[0]

        for e in self.exercicio_digrafos:
            self.responde_exercicio(aluno, e, 0)

        for e in self.exercicio_silabas:
            self.responde_exercicio(aluno, e, 1)

        self.assertEqual(Resposta.objects.all().count(), 10)

        print(
            queries.desempenho_serie_disciplina_por_assunto(
                self.turma.id, 5, self.portugues.id
            ))


class FixturedTestCase(TestCase):
    """
    Nova classe de teste de métodos da test_queries
    """
    fixtures = ['test.db.json']

    def tearDown(self):
        Resposta.objects.all().delete()

    def test_consulta_analitica_por_serie_prova_brasil_sem_resposta(self):
        escola = Escola.objects.get(pk=2)
        serie = 5

        r = queries.consulta_analitica_por_serie_prova_brasil(
            escola.id, serie)
        self.assertEqual(0, r.count())

    def test_consulta_analitica_por_serie_prova_brasil_com_respostas(self):
        albus = Aluno.objects.get(pk=8)
        exercicio = Exercicio.objects.get(pk=17)  # Frações numéricas
        alternativas = Alternativa.objects.filter(exercicio=exercicio)
        Resposta.aplicar_resposta(albus, exercicio, alternativas[0])

        escola = Escola.objects.get(pk=4)
        serie = 5

        r = queries.consulta_analitica_por_serie_prova_brasil(
            escola.id, serie)
        self.assertEqual(1, r.count())
        self.assertEqual(r[0]['exercicio__aula__disciplina__nome'], 'Matemática')
        self.assertEqual(r[0]['corretas'], 1)
        self.assertEqual(r[0]['erradas'], 0)

    def test_consulta_analitica_por_serie_super_reforco_sem_respostas(self):
        escola = Escola.objects.get(pk=2)
        serie = 5

        r = queries.consulta_analitica_por_serie_super_reforco(
            escola.id, serie)
        self.assertEqual(0, r.count())

    def test_consulta_analitica_por_serie_super_reforco_com_respostas(self):
        albus = Aluno.objects.get(pk=8)
        exercicio = Exercicio.objects.get(pk=3)  # Colonização do Brasil
        alternativas = Alternativa.objects.filter(exercicio=exercicio)
        Resposta.aplicar_resposta(albus, exercicio, alternativas[0])

        escola = Escola.objects.get(pk=4)
        serie = 5

        r = queries.consulta_analitica_por_serie_super_reforco(
            escola.id, serie)
        self.assertEqual(1, r.count())
        self.assertEqual(r[0]['exercicio__aula__disciplina__nome'], 'História')
        self.assertEqual(r[0]['corretas'], 1)
        self.assertEqual(r[0]['erradas'], 0)


class VimeoTestCase(TestCase):

    def test_about_me(self):
        print(vimeo.about_me().json())

    def test_picutes(self):
        print(vimeo.pictures(256358890))
