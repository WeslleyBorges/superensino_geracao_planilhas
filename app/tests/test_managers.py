from django.test import TestCase
from app.models import Resposta, Aula
from app.models import Aluno
from app.models import Exercicio, Disciplina
from app.models import Alternativa
from app.models import Escola, HistoricoAulasAssistidas
from app import services


class RespostaQuerySetTestCase(TestCase):
    fixtures = ['test.db.json']

    def setUp(self):
        # Aluno da Escola Municipal Professor Paulo Graça (5o Ano B)
        aluno = Aluno.objects.get(user__username='aslam')

        # Aluno da Escola Municipal Professor Paulo Graça (5o Ano A)
        apollo = Aluno.objects.get(user__username='apollo')

        # Aluno da escola Nísia Floresta Brasileira Augusta
        self.charlie = Aluno.objects.get(user__username='charlie')
        # Escola Nísia Floresta Brasileira Augusta
        self.nisia_floresta_brasileira_augusta = Escola.objects.get(pk=3)
        # Escola Municipal Professor Paulo Graça
        self.paulo_garca = Escola.objects.get(pk=4)

        # Exercicios de matemática de reforço
        ex1 = Exercicio.objects.get(pk=2)
        a1 = Alternativa.objects.filter(exercicio=ex1)
        ex2 = Exercicio.objects.get(pk=15)
        a2 = Alternativa.objects.filter(exercicio=ex2)
        ex3 = Exercicio.objects.get(pk=16)
        a3 = Alternativa.objects.filter(exercicio=ex3)

        # Exercicios de portugues de reforço
        pt_ex1 = Exercicio.objects.get(pk=6)
        pt_a1 = Alternativa.objects.filter(exercicio=pt_ex1)
        pt_ex2 = Exercicio.objects.get(pk=7)
        pt_a2 = Alternativa.objects.filter(exercicio=pt_ex2)
        pt_ex3 = Exercicio.objects.get(pk=8)
        pt_a3 = Alternativa.objects.filter(exercicio=pt_ex3)

        # Exercícios de matemática prova Brasil
        pb_ex1 = Exercicio.objects.get(pk=17)
        pb_a1 = Alternativa.objects.filter(exercicio=pb_ex1)
        pb_ex2 = Exercicio.objects.get(pk=18)
        pb_a2 = Alternativa.objects.filter(exercicio=pb_ex2)
        pb_ex3 = Exercicio.objects.get(pk=19)
        pb_a3 = Alternativa.objects.filter(exercicio=pb_ex3)

        # Exercicios de matemática de reforço (6o Ano)
        mt_ex1 = Exercicio.objects.get(pk=20)
        mt_a1 = Alternativa.objects.filter(exercicio=mt_ex1)

        Resposta.aplicar_resposta(aluno, ex1, a1[0])
        Resposta.aplicar_resposta(aluno, ex2, a2[0])
        Resposta.aplicar_resposta(aluno, ex3, a3[0])
        Resposta.aplicar_resposta(self.charlie, ex3, a3[1])

        Resposta.aplicar_resposta(aluno, pb_ex1, pb_a1[0])
        Resposta.aplicar_resposta(aluno, pb_ex2, pb_a2[0])
        Resposta.aplicar_resposta(aluno, pb_ex3, pb_a3[0])

        Resposta.aplicar_resposta(aluno, pt_ex1, pt_a1[0])
        Resposta.aplicar_resposta(aluno, pt_ex2, pt_a2[0])
        Resposta.aplicar_resposta(aluno, pt_ex3, pt_a3[0])

        Resposta.aplicar_resposta(aluno, mt_ex1, mt_a1[0])

        # Respostas Apollo
        Resposta.aplicar_resposta(apollo, ex1, a1[0])
        Resposta.aplicar_resposta(apollo, ex2, a2[0])
        Resposta.aplicar_resposta(apollo, ex3, a3[0])

        Resposta.aplicar_resposta(apollo, pb_ex1, pb_a1[0])
        Resposta.aplicar_resposta(apollo, pb_ex2, pb_a2[0])
        Resposta.aplicar_resposta(apollo, pb_ex3, pb_a3[0])

        Resposta.aplicar_resposta(apollo, pt_ex1, pt_a1[1])
        Resposta.aplicar_resposta(apollo, pt_ex2, pt_a2[1])
        Resposta.aplicar_resposta(apollo, pt_ex3, pt_a3[1])

    def test_desempenho_6_serie_superreforco(self):
        """Verifica se o SE recupera o desempenho por serie."""
        rs = Resposta.objects.desempenho_serie(self.paulo_garca.id, 6, False)
        self.assertEqual(rs[0]['exercicio__aula__disciplina'], 1)
        self.assertEqual(rs[0]['corretas'], 1)
        self.assertEqual(rs[0]['erradas'], 0)

    def test_desempenho_5_serie_superreforco(self):
        """Verifica se o SE recupera o desempenho por serie."""
        rs = Resposta.objects.desempenho_serie(self.paulo_garca.id, 5, False)
        self.assertEqual(rs[0]['exercicio__aula__disciplina'], 1)
        self.assertEqual(rs[0]['corretas'], 3)
        self.assertEqual(rs[0]['erradas'], 0)

        self.assertEqual(rs[1]['exercicio__aula__disciplina'], 2)
        self.assertEqual(rs[1]['corretas'], 3)
        self.assertEqual(rs[1]['erradas'], 0)

    def test_desempenho_serie_provabrasil(self):
        """Verifica se o SE recupera o desempenho por serie da PB."""
        rs = Resposta.objects.desempenho_serie(self.paulo_garca.id, 5, True)
        self.assertEqual(rs[0]['exercicio__aula__disciplina'], 7)
        self.assertEqual(rs[0]['corretas'], 3)
        self.assertEqual(rs[0]['erradas'], 0)

    def test_select_reposta_by_escola(self):
        rs = Resposta.objects.escola(self.nisia_floresta_brasileira_augusta.id)
        self.assertEqual(1, rs.count())

    def test_desempenho_turmas(self):
        """Verifica se o SE recupera o desempenho por serie."""
        rs = Resposta.objects.desempenho_turmas(self.paulo_garca.id, 5, False)

        self.assertEqual(rs[0]['aluno__turma'], 4)
        self.assertEqual(rs[0]['aluno__turma__identificador'], '5o Ano A')
        self.assertEqual(rs[0]['aproveitamento'], 50)

        self.assertEqual(rs[1]['aluno__turma'], 5)
        self.assertEqual(rs[1]['aluno__turma__identificador'], '5o Ano B')
        self.assertEqual(rs[1]['aproveitamento'], 100)


class ServicesTestCase(TestCase):
    fixtures = ['test.db.json']

    def setUp(self):
        # Aluno da Escola Municipal Professor Paulo Graça (5o Ano B)
        self.aslam = Aluno.objects.get(user__username='aslam')

        # Aluno da Escola Municipal Professor Paulo Graça (5o Ano A)
        self.apollo = Aluno.objects.get(user__username='apollo')

        # Aluno da escola Nísia Floresta Brasileira Augusta
        self.charlie = Aluno.objects.get(user__username='charlie')
        # Escola Nísia Floresta Brasileira Augusta
        self.nisia_floresta_brasileira_augusta = Escola.objects.get(pk=3)
        # Escola Municipal Professor Paulo Graça
        self.paulo_garca = Escola.objects.get(pk=4)

        # Exercicios de matemática de reforço
        ex1 = Exercicio.objects.get(pk=2)
        a1 = Alternativa.objects.filter(exercicio=ex1)
        ex2 = Exercicio.objects.get(pk=15)
        a2 = Alternativa.objects.filter(exercicio=ex2)
        ex3 = Exercicio.objects.get(pk=16)
        a3 = Alternativa.objects.filter(exercicio=ex3)

        # Exercicios de portugues de reforço
        pt_ex1 = Exercicio.objects.get(pk=6)
        pt_a1 = Alternativa.objects.filter(exercicio=pt_ex1)
        pt_ex2 = Exercicio.objects.get(pk=7)
        pt_a2 = Alternativa.objects.filter(exercicio=pt_ex2)
        pt_ex3 = Exercicio.objects.get(pk=8)
        pt_a3 = Alternativa.objects.filter(exercicio=pt_ex3)

        # Exercícios de matemática prova Brasil
        pb_ex1 = Exercicio.objects.get(pk=17)
        pb_a1 = Alternativa.objects.filter(exercicio=pb_ex1)
        pb_ex2 = Exercicio.objects.get(pk=18)
        pb_a2 = Alternativa.objects.filter(exercicio=pb_ex2)
        pb_ex3 = Exercicio.objects.get(pk=19)
        pb_a3 = Alternativa.objects.filter(exercicio=pb_ex3)

        # Exercicios de matemática de reforço (6o Ano)
        mt_ex1 = Exercicio.objects.get(pk=20)
        mt_a1 = Alternativa.objects.filter(exercicio=mt_ex1)

        Resposta.aplicar_resposta(self.aslam, ex1, a1[0])
        Resposta.aplicar_resposta(self.aslam, ex2, a2[0])
        Resposta.aplicar_resposta(self.aslam, ex3, a3[0])
        Resposta.aplicar_resposta(self.charlie, ex3, a3[1])

        Resposta.aplicar_resposta(self.aslam, pb_ex1, pb_a1[0])
        Resposta.aplicar_resposta(self.aslam, pb_ex2, pb_a2[0])
        Resposta.aplicar_resposta(self.aslam, pb_ex3, pb_a3[0])

        Resposta.aplicar_resposta(self.aslam, pt_ex1, pt_a1[0])
        Resposta.aplicar_resposta(self.aslam, pt_ex2, pt_a2[0])
        Resposta.aplicar_resposta(self.aslam, pt_ex3, pt_a3[0])

        Resposta.aplicar_resposta(self.aslam, mt_ex1, mt_a1[0])

        # Respostas Apollo
        Resposta.aplicar_resposta(self.apollo, ex1, a1[0])
        Resposta.aplicar_resposta(self.apollo, ex2, a2[0])
        Resposta.aplicar_resposta(self.apollo, ex3, a3[0])

        Resposta.aplicar_resposta(self.apollo, pb_ex1, pb_a1[0])
        Resposta.aplicar_resposta(self.apollo, pb_ex2, pb_a2[0])
        Resposta.aplicar_resposta(self.apollo, pb_ex3, pb_a3[0])

        Resposta.aplicar_resposta(self.apollo, pt_ex1, pt_a1[1])
        Resposta.aplicar_resposta(self.apollo, pt_ex2, pt_a2[1])
        Resposta.aplicar_resposta(self.apollo, pt_ex3, pt_a3[1])

    def tearDown(self):
        Resposta.objects.all().delete()
        HistoricoAulasAssistidas.objects.all().delete()

    def test_get_desempenho_individual_por_disciplina_sumario_geral(self):
        # Exercícios adicionais de números primos
        ex4 = Exercicio.objects.get(pk=21)
        a4 = Alternativa.objects.filter(exercicio=ex4)
        ex5 = Exercicio.objects.get(pk=22)
        a5 = Alternativa.objects.filter(exercicio=ex5)

        Resposta.aplicar_resposta(self.aslam, ex4, a4[0])
        Resposta.aplicar_resposta(self.aslam, ex5, a5[1])

        # Matemática Super Reforço(sr)
        matematica_sr = Disciplina.objects.get(pk=1)
        serie = 5
        bimestre = 1
        is_prova_brasil = False

        data = services.get_desempenho_individual_por_disciplina(
            self.aslam,
            matematica_sr,
            serie,
            bimestre,
            is_prova_brasil)

        self.assertEqual(data['disciplina_id'], matematica_sr.id)
        self.assertEqual(data['disciplina_nome'], matematica_sr.nome)
        self.assertEqual(data['total_aulas'], 3)
        self.assertEqual(data['aulas_assistidas'], 0)
        self.assertEqual(data['total_exercicios'], 5)
        self.assertEqual(data['exercicios_realizados'], 5)
        self.assertEqual(data['num_acertos'], 4)

    def test_get_desempenho_individual_por_disciplina_detalhes(self):
        # Exercícios adicionais de números primos
        ex4 = Exercicio.objects.get(pk=21)
        a4 = Alternativa.objects.filter(exercicio=ex4)
        ex5 = Exercicio.objects.get(pk=22)
        a5 = Alternativa.objects.filter(exercicio=ex5)

        Resposta.aplicar_resposta(self.aslam, ex4, a4[0])
        Resposta.aplicar_resposta(self.aslam, ex5, a5[1])

        # Matemática Super Reforço(sr)
        matematica_sr = Disciplina.objects.get(pk=1)
        serie = 5
        bimestre = 1
        is_prova_brasil = False

        data = services.get_desempenho_individual_por_disciplina(
            self.aslam,
            matematica_sr,
            serie,
            bimestre,
            is_prova_brasil)['assuntos']

        self.assertEqual(data[0]['assunto_id'], 2)
        self.assertEqual(data[0]['assunto_nome'], 'Frações')
        self.assertEqual(data[0]['total_aulas'], 1)
        self.assertEqual(data[0]['aulas_assistidas'], 0)
        self.assertEqual(data[0]['total_exercicios'], 3)
        self.assertEqual(data[0]['exercicios_realizados'], 3)
        self.assertEqual(data[0]['num_acertos'], 3)

        self.assertEqual(data[1]['assunto_id'], 3)
        self.assertEqual(data[1]['assunto_nome'], 'Números Primos')
        self.assertEqual(data[1]['total_aulas'], 1)
        self.assertEqual(data[1]['aulas_assistidas'], 0)
        self.assertEqual(data[1]['total_exercicios'], 2)
        self.assertEqual(data[1]['exercicios_realizados'], 2)
        self.assertEqual(data[1]['num_acertos'], 1)

    def test_get_historico_aulas_assitidas_serie(self):
        # Assiste uma aula de frações
        fracoes = Aula.objects.get(assunto='Frações')
        video_fracoes = fracoes.attachments.first()
        HistoricoAulasAssistidas.register_viewing(
                aula=fracoes, attachment=video_fracoes, aluno=self.aslam)

        HistoricoAulasAssistidas.register_viewing(
                aula=fracoes, attachment=video_fracoes, aluno=self.apollo)

        HistoricoAulasAssistidas.register_viewing(
                aula=fracoes, attachment=video_fracoes, aluno=self.charlie)

        data = services.get_historico_aulas_assitidas_serie(
            self.paulo_garca, 5).count()

        # for d in data:
        #     print(d.aluno.turma_set.first())
        # services.get_serie_summary(self.paulo_garca, 5)
        self.assertEqual(data, 2)
        # print(data)

    def test_get_serie_summary(self):
        # Assiste uma aula de frações
        fracoes = Aula.objects.get(assunto='Frações')
        video_fracoes = fracoes.attachments.first()
        HistoricoAulasAssistidas.register_viewing(
                aula=fracoes, attachment=video_fracoes, aluno=self.aslam)

        HistoricoAulasAssistidas.register_viewing(
                aula=fracoes, attachment=video_fracoes, aluno=self.apollo)

        HistoricoAulasAssistidas.register_viewing(
                aula=fracoes, attachment=video_fracoes, aluno=self.charlie)

        data = services.get_serie_summary(self.paulo_garca, 5)
        self.assertEqual(data['aulas_assistidas'], 2)
