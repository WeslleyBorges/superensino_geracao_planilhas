from django.test import TestCase

from app.models import Disciplina, Turma, Escola, Exercicio
from core.tests import SuperEnsinoDataMixin, DataUtils
from data.wharehouse import services
from data.wharehouse.models import ExercisesDataWharehouse


class ServicesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        mixin = SuperEnsinoDataMixin()
        mixin.setup_data()

        turma_5a = Turma.objects.get(identificador='5a', escola__id=1)
        turma_5b = Turma.objects.get(identificador='5b', escola__id=1)
        turma_6a = Turma.objects.get(identificador='6a', escola__id=1)
        turma_6b = Turma.objects.get(identificador='6b', escola__id=1)

        DataUtils.turma_responde_exercicios(turma_5a, 6)
        DataUtils.turma_responde_exercicios(turma_5b, 4)
        DataUtils.turma_responde_exercicios(turma_6a, 8)
        DataUtils.turma_responde_exercicios(turma_6b, 2)

        # Descomente para imprimir o conteúdo do datawharehouse em um csv
        # DataUtils.export_datawharehouse_to_csv()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.escola = Escola.objects.get(nome='Super Ensino')
        self.turma_5a = Turma.objects.get(identificador='5a', escola__id=1)

    def test_get_desempenho_series(self):
        rs = services.get_desempenho_series(self.escola)
        self.assertEqual(rs[0], {'escola': 1, 'serie': 5, 'acertos': 2500, 'ttl_exercicios': 5000, 'indice': 50})
        self.assertEqual(rs[1], {'escola': 1, 'serie': 6, 'acertos': 1500, 'ttl_exercicios': 3000, 'indice': 50})

    def test_get_desempenho_disciplinas_filtrado_por_serie(self):
        rs = services.get_desempenho_disciplinas_filtrado_por_serie(self.escola, 5, False)
        self.assertEqual(rs[0], {'disciplina': 3, 'acertos': 500, 'ttl_exercicios': 1000, 'indice': 50})
        self.assertEqual(rs[1], {'disciplina': 4, 'acertos': 500, 'ttl_exercicios': 1000, 'indice': 50})
        self.assertEqual(rs[2], {'disciplina': 5, 'acertos': 500, 'ttl_exercicios': 1000, 'indice': 50})

    def test_get_desempenho_assuntos_filtrado_por_disciplina(self):
        disciplina = Disciplina.objects.get(nome='Matemática', is_prova_brasil=False)

        rs = services.get_desempenho_assuntos_filtrado_por_disciplina(self.escola, disciplina)
        rs = [x for x in rs]
        self.assertEqual(rs, [{'exercicio__aula__id': 51, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 52, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 53, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 54, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 55, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 56, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 57, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 58, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 59, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 60, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 81, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 82, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 83, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 84, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 85, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 86, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 87, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 88, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 89, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50},
         {'exercicio__aula__id': 90, 'acertos': 50, 'ttl_exercicios': 100, 'indice': 50}])

    def test_get_desempenho_turmas_filtrado_por_serie(self):
        rs = services.get_desempenho_turmas_filtrado_por_serie(self.escola, 5, False)
        rs = [x for x in rs]
        self.assertEqual(rs, [
            {'turma': 1, 'acertos': 900, 'ttl_exercicios': 1500, 'indice': 60},
            {'turma': 2, 'acertos': 600, 'ttl_exercicios': 1500, 'indice': 40}])

    def test_get_desempenho_disciplinas_filtrado_por_turma(self):
        rs = services.get_desempenho_disciplinas_filtrado_por_turma(self.escola, self.turma_5a, False)
        rs = [x for x in rs]
        self.assertEqual(rs, [
            {'disciplina': 3, 'acertos': 300, 'ttl_exercicios': 500, 'indice': 60},
            {'disciplina': 4, 'acertos': 300, 'ttl_exercicios': 500, 'indice': 60},
            {'disciplina': 5, 'acertos': 300, 'ttl_exercicios': 500, 'indice': 60}])

    def test_get_desempenho_assuntos_filtrado_por_disciplina_e_turma(self):
        disciplina = Disciplina.objects.get(nome='Matemática', is_prova_brasil=False)

        rs = services.get_desempenho_assuntos_filtrado_por_disciplina_e_turma(self.escola, disciplina, self.turma_5a)
        self.assertEqual(rs[0], {'exercicio__aula__id': 51, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})
        self.assertEqual(rs[1], {'exercicio__aula__id': 52, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})
        self.assertEqual(rs[2], {'exercicio__aula__id': 53, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})
        self.assertEqual(rs[3], {'exercicio__aula__id': 54, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})
        self.assertEqual(rs[4], {'exercicio__aula__id': 55, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})
        self.assertEqual(rs[5], {'exercicio__aula__id': 56, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})
        self.assertEqual(rs[6], {'exercicio__aula__id': 57, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})
        self.assertEqual(rs[7], {'exercicio__aula__id': 58, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})
        self.assertEqual(rs[8], {'exercicio__aula__id': 59, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})
        self.assertEqual(rs[9], {'exercicio__aula__id': 60, 'acertos': 30, 'ttl_exercicios': 50, 'indice': 60})

    def test_get_desempenho_alunos_reforco_filtrado_por_turma(self):
        qs = services.get_desempenho_alunos_reforco_filtrado_por_turma(self.turma_5a, False)

        # self.assertEqual(qs, [
        self.assertEqual(qs[0], {'exercisesdatawharehouse__aluno': 3, 'acertos': 180, 'ttl_exercicios': 300, 'indice': 60})
        self.assertEqual(qs[1], {'exercisesdatawharehouse__aluno': 4, 'acertos': 180, 'ttl_exercicios': 300, 'indice': 60})
        self.assertEqual(qs[2], {'exercisesdatawharehouse__aluno': 5, 'acertos': 180, 'ttl_exercicios': 300, 'indice': 60})
        self.assertEqual(qs[3], {'exercisesdatawharehouse__aluno': 6, 'acertos': 180, 'ttl_exercicios': 300, 'indice': 60})
        self.assertEqual(qs[4], {'exercisesdatawharehouse__aluno': 7, 'acertos': 180, 'ttl_exercicios': 300, 'indice': 60})


class ExercisesDataWharehouseTests(TestCase):
    @classmethod
    def setUpClass(cls):
        mixin = SuperEnsinoDataMixin()
        mixin.setup_data()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.turma_5a = Turma.objects.get(identificador='5a', escola__id=1)
        self.exercicios = Exercicio.objects.filter(aula__serie=self.turma_5a.serie)

    def test_avoid_duplicate(self):
        ExercisesDataWharehouse.add(
            self.turma_5a.alunos.all()[0],
            self.exercicios[0],
            self.exercicios[0].alternativas.all()[0]
        )
        ExercisesDataWharehouse.add(
            self.turma_5a.alunos.all()[0],
            self.exercicios[0],
            self.exercicios[0].alternativas.all()[1]
        )

        queryset = ExercisesDataWharehouse.objects.all()
        self.assertEqual(1, queryset.count())
        self.assertEqual(queryset[0].resposta, self.exercicios[0].alternativas.all()[0])


# class HelpersTests(SuperEnsinoWithFixturesTestCase):
#     """Class para a validação de funções do módulo helpers.py."""
#
#     def setUp(self):
#         super().setUp()
#
#
#     def test_calculate_turma_details(self):
#         """Verifica se o método traz corretamente todos os detalhes especificados
#         para retorno. Para esse teste é considerado a disciplina de história para
#         5o Ano A da escola Super Ensino, primeiro bimestre."""
#         bim = 1
#
#         # Simula a resolução de exercícios para geração de estatísticas
#         self.responder(self.daniel, self.historia, 10, 5)
#         self.responder(self.maria, self.historia, 10, 3)
#
#         ## Responde igualmente no 2 bimestre
#         self.responder(self.pedro, self.historia, 10, 5, 2)
#         self.responder(self.daniel, self.historia, 10, 5, 2)
#         self.responder(self.maria, self.historia, 10, 3, 2)
#
#         # outra turma
#         self.responder(self.renata, self.historia, 10, 7)
#
#         # Simula a visualização de vídeos para geração de estatísticas. Cada um
#         # assite 3 videos.
#         utils.visualize_aula(self.historia, bim, self.pedro, 3)
#         utils.visualize_aula(self.historia, bim, self.daniel, 3)
#         utils.visualize_aula(self.historia, bim, self.maria, 3)
#
#         data = helpers.calculate_turma_details(
#             self._5anoA_SuperEnsino, self.historia)
#
#         print(data)
#
#     def test_consulta_turmas_professor_uma_turma_unico_aluno(self):
#         """
#         Testa se os cálculos estão sendo feitos corretamente utilizando apenas um aluno.
#
#         Codições:
#             - Apenas um aluno
#             - Única turma
#         """
#
#         # Configuração do cenário de teste
#         exercios_hist_resolvidos_pedro = 10
#         exercios_hist_resolvidos_acertos_pedro = 2
#         exercios_hist_resolvidos_erros_pedro = exercios_hist_resolvidos_pedro - exercios_hist_resolvidos_acertos_pedro
#         aproveitamento_pedro = utils.calculate_aproveitamento(
#             exercios_hist_resolvidos_pedro, exercios_hist_resolvidos_acertos_pedro)
#
#         # Assegura que estamos iniciando os testes com um log de exercícios zerado.
#         assert (ExercisesDataWharehouse.objects.all().count() == 0)
#
#         # Simula a resolução de exercícios.
#         self.responder(
#             self.pedro, self.historia, exercios_hist_resolvidos_pedro,
#             exercios_hist_resolvidos_acertos_pedro)
#
#         rs= helpers.consulta_turmas_professor(
#             self.prof_rose, self._5anoA_SuperEnsino.escola)
#
#         self.assertEquals(rs[0]['turma'], self._5anoA_SuperEnsino.identificador)
#         self.assertEquals(rs[0]['turmaId'], self._5anoA_SuperEnsino.id)
#         self.assertEquals(rs[0]['indice'], aproveitamento_pedro)
#         self.assertEquals(rs[0]['disciplina'], self.historia.nome)
#         self.assertEquals(rs[0]['disciplinaId'], self.historia.id)
#         self.assertEquals(rs[0]['escola'], self._5anoA_SuperEnsino.escola.nome)
#         self.assertEquals(rs[0]['totalAcertos'], exercios_hist_resolvidos_acertos_pedro)
#         self.assertEquals(rs[0]['totalErros'], exercios_hist_resolvidos_erros_pedro)
#         self.assertEquals(rs[0]['maxNota'], aproveitamento_pedro)
#         self.assertEquals(rs[0]['minNota'], aproveitamento_pedro)
#         self.assertEquals(rs[0]['exerciciosResolvidos'], exercios_hist_resolvidos_pedro)
#         self.assertEquals(rs[0]['totalExercicios'], 25)
#         self.assertEquals(rs[0]['classificacaoDisciplina'], 1)
#         self.assertEquals(rs[0]['totalDisciplina'], 1)
#
#     def test_consulta_turmas_professor_uma_turma_tres_alunos(self):
#         data = [
#             {
#                 'aluno': self.pedro,
#                 'disciplina': self.historia,
#                 'exercicios_realizados': 10,
#                 'acertos': 2,
#                 'erros': 8,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 2) # 20%
#             },
#             {
#                 'aluno': self.daniel,
#                 'disciplina': self.historia,
#                 'exercicios_realizados': 10,
#                 'acertos': 5,
#                 'erros': 5,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 5) # 50%
#             },
#             {
#                 'aluno': self.maria,
#                 'disciplina': self.historia,
#                 'exercicios_realizados': 10,
#                 'acertos': 8,
#                 'erros': 2,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 8) # 80%
#             }
#         ]
#
#         # Assegura que estamos iniciando os testes com um log de exercícios zerado.
#         assert (ExercisesDataWharehouse.objects.all().count() == 0)
#
#         total_exercicios_realizados = 0
#         total_acertos = 0
#         total_erros = 0
#         melhor_desempenho = 80 # aluna Maria
#         pior_desempenho = 20 # aluno Pedro
#
#         for d in data:
#             # Simula a resolução de exercícios.
#             self.responder(
#                 d['aluno'], d['disciplina'], d['exercicios_realizados'],
#                 d['acertos'])
#             total_exercicios_realizados += d['exercicios_realizados']
#             total_acertos += d['acertos']
#             total_erros += d['erros']
#
#         indice_turma = utils.calculate_aproveitamento(total_exercicios_realizados, total_acertos)
#
#         rs= helpers.consulta_turmas_professor(
#             self.prof_rose, self._5anoA_SuperEnsino.escola)
#
#         self.assertEquals(rs[0]['turma'], self._5anoA_SuperEnsino.identificador)
#         self.assertEquals(rs[0]['turmaId'], self._5anoA_SuperEnsino.id)
#         self.assertEquals(rs[0]['indice'], indice_turma)
#         self.assertEquals(rs[0]['disciplina'], self.historia.nome)
#         self.assertEquals(rs[0]['disciplinaId'], self.historia.id)
#         self.assertEquals(rs[0]['escola'], self._5anoA_SuperEnsino.escola.nome)
#         self.assertEquals(rs[0]['totalAcertos'], total_acertos)
#         self.assertEquals(rs[0]['totalErros'], total_erros)
#         self.assertEquals(rs[0]['maxNota'], melhor_desempenho)
#         self.assertEquals(rs[0]['minNota'], pior_desempenho)
#         self.assertEquals(rs[0]['exerciciosResolvidos'], total_exercicios_realizados)
#         self.assertEquals(rs[0]['totalExercicios'], 25)
#         self.assertEquals(rs[0]['classificacaoDisciplina'], 1)
#         self.assertEquals(rs[0]['totalDisciplina'], 1)
#
#     def test_consulta_turmas_professor_uma_turma_tres_alunos_duas_disciplinas(self):
#         """
#         Testando o cenário em que um professor leciona duas disciplinas para a
#         mesma turma turma. O objetivo desse teste é verificar se as métricas de
#         cada turma permanecem isoladas.
#         """
#         data_historia = [
#             {
#                 'aluno': self.pedro,
#                 'disciplina': self.historia,
#                 'exercicios_realizados': 10,
#                 'acertos': 2,
#                 'erros': 8,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 2) # 20%
#             },
#             {
#                 'aluno': self.daniel,
#                 'disciplina': self.historia,
#                 'exercicios_realizados': 10,
#                 'acertos': 5,
#                 'erros': 5,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 5) # 50%
#             },
#             {
#                 'aluno': self.maria,
#                 'disciplina': self.historia,
#                 'exercicios_realizados': 10,
#                 'acertos': 8,
#                 'erros': 2,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 8) # 80%
#             },
#         ]
#
#         data_geografia = [
#             {
#                 'aluno': self.pedro,
#                 'disciplina': self.geografia,
#                 'exercicios_realizados': 10,
#                 'acertos': 9,
#                 'erros': 1,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 9) # 90%
#             },
#             {
#                 'aluno': self.daniel,
#                 'disciplina': self.geografia,
#                 'exercicios_realizados': 10,
#                 'acertos': 5,
#                 'erros': 5,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 5) # 50%
#             },
#             {
#                 'aluno': self.maria,
#                 'disciplina': self.geografia,
#                 'exercicios_realizados': 10,
#                 'acertos': 8,
#                 'erros': 2,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 8) # 80%
#             }
#         ]
#
#         # Assegura que estamos iniciando os testes com um log de exercícios zerado.
#         assert (ExercisesDataWharehouse.objects.all().count() == 0)
#
#         total_exercicios_realizados_hist = 0
#         total_acertos_hist = 0
#         total_erros_hist = 0
#         melhor_desempenho_hist = 80 # aluna Maria
#         pior_desempenho_hist = 20 # aluno Pedro
#
#         for d in data_historia:
#             # Simula a resolução de exercícios.
#             self.responder(
#                 d['aluno'], d['disciplina'], d['exercicios_realizados'],
#                 d['acertos'])
#             total_exercicios_realizados_hist += d['exercicios_realizados']
#             total_acertos_hist += d['acertos']
#             total_erros_hist += d['erros']
#
#         indice_turma_hist = utils.calculate_aproveitamento(total_exercicios_realizados_hist, total_acertos_hist)
#
#         total_exercicios_realizados_geo = 0
#         total_acertos_geo = 0
#         total_erros_geo = 0
#         melhor_desempenho_geo = 90 # aluna Maria
#         pior_desempenho_geo = 50 # aluno Pedro
#
#         for d in data_geografia:
#             # Simula a resolução de exercícios.
#             self.responder(
#                 d['aluno'], d['disciplina'], d['exercicios_realizados'],
#                 d['acertos'])
#             total_exercicios_realizados_geo += d['exercicios_realizados']
#             total_acertos_geo += d['acertos']
#             total_erros_geo += d['erros']
#
#         indice_turma_geo = utils.calculate_aproveitamento(total_exercicios_realizados_geo, total_acertos_geo)
#
#         rs= helpers.consulta_turmas_professor(
#             self.prof_rose, self._5anoA_SuperEnsino.escola)
#
#         self.assertEquals(rs[0]['turma'], self._5anoA_SuperEnsino.identificador)
#         self.assertEquals(rs[0]['turmaId'], self._5anoA_SuperEnsino.id)
#         self.assertEquals(rs[0]['indice'], indice_turma_hist)
#         self.assertEquals(rs[0]['disciplina'], self.historia.nome)
#         self.assertEquals(rs[0]['disciplinaId'], self.historia.id)
#         self.assertEquals(rs[0]['escola'], self._5anoA_SuperEnsino.escola.nome)
#         self.assertEquals(rs[0]['totalAcertos'], total_acertos_hist)
#         self.assertEquals(rs[0]['totalErros'], total_erros_hist)
#         self.assertEquals(rs[0]['maxNota'], melhor_desempenho_hist)
#         self.assertEquals(rs[0]['minNota'], pior_desempenho_hist)
#         self.assertEquals(rs[0]['exerciciosResolvidos'], total_exercicios_realizados_hist)
#         self.assertEquals(rs[0]['totalExercicios'], 25)
#         self.assertEquals(rs[0]['classificacaoDisciplina'], 1)
#         self.assertEquals(rs[0]['totalDisciplina'], 1)
#
#         self.assertEquals(rs[1]['turma'], self._5anoA_SuperEnsino.identificador)
#         self.assertEquals(rs[1]['turmaId'], self._5anoA_SuperEnsino.id)
#         self.assertEquals(rs[1]['indice'], indice_turma_geo)
#         self.assertEquals(rs[1]['disciplina'], self.geografia.nome)
#         self.assertEquals(rs[1]['disciplinaId'], self.geografia.id)
#         self.assertEquals(rs[1]['escola'], self._5anoA_SuperEnsino.escola.nome)
#         self.assertEquals(rs[1]['totalAcertos'], total_acertos_geo)
#         self.assertEquals(rs[1]['totalErros'], total_erros_geo)
#         self.assertEquals(rs[1]['maxNota'], melhor_desempenho_geo)
#         self.assertEquals(rs[1]['minNota'], pior_desempenho_geo)
#         self.assertEquals(rs[1]['exerciciosResolvidos'], total_exercicios_realizados_geo)
#         self.assertEquals(rs[1]['totalExercicios'], 25)
#         self.assertEquals(rs[1]['classificacaoDisciplina'], 1)
#         self.assertEquals(rs[1]['totalDisciplina'], 1)
#
#     def test_consulta_turmas_professor_atuando_em_duas_escolas(self):
#         """
#         Esse teste verifica se a query está realmente filtrado os dados por
#         escola.
#         """
#
#         # Configuração do cenário de teste
#         exercios_hist_resolvidos_pedro = 10
#         exercios_hist_resolvidos_acertos_pedro = 2
#         exercios_hist_resolvidos_erros_pedro = exercios_hist_resolvidos_pedro - exercios_hist_resolvidos_acertos_pedro
#         aproveitamento_pedro = utils.calculate_aproveitamento(
#             exercios_hist_resolvidos_pedro, exercios_hist_resolvidos_acertos_pedro)
#
#         # Assegura que estamos iniciando os testes com um log de exercícios zerado.
#         assert (ExercisesDataWharehouse.objects.all().count() == 0)
#
#         # Simula a resolução de exercícios.
#         self.responder(
#             self.pedro, self.historia, exercios_hist_resolvidos_pedro,
#             exercios_hist_resolvidos_acertos_pedro)
#
#         # Respostas adicionadas pela aluna de Hogwarts renata, que não devem ser computadas
#         # nos dados da Super Ensino
#         self.responder(
#             self.renata, self.geografia, 10, 2)
#
#         rs= helpers.consulta_turmas_professor(
#             self.prof_rose, self._5anoA_SuperEnsino.escola)
#
#         self.assertEquals(rs[0]['turma'], self._5anoA_SuperEnsino.identificador)
#         self.assertEquals(rs[0]['turmaId'], self._5anoA_SuperEnsino.id)
#         self.assertEquals(rs[0]['indice'], aproveitamento_pedro)
#         self.assertEquals(rs[0]['disciplina'], self.historia.nome)
#         self.assertEquals(rs[0]['disciplinaId'], self.historia.id)
#         self.assertEquals(rs[0]['escola'], self._5anoA_SuperEnsino.escola.nome)
#         self.assertEquals(rs[0]['totalAcertos'], exercios_hist_resolvidos_acertos_pedro)
#         self.assertEquals(rs[0]['totalErros'], exercios_hist_resolvidos_erros_pedro)
#         self.assertEquals(rs[0]['maxNota'], aproveitamento_pedro)
#         self.assertEquals(rs[0]['minNota'], aproveitamento_pedro)
#         self.assertEquals(rs[0]['exerciciosResolvidos'], exercios_hist_resolvidos_pedro)
#         self.assertEquals(rs[0]['totalExercicios'], 25)
#         self.assertEquals(rs[0]['classificacaoDisciplina'], 1)
#         self.assertEquals(rs[0]['totalDisciplina'], 1)
#
#     def test_consulta_turmas_professor_atuacao_do_professor_em_apenas_uma_turma(self):
#         """
#         Nesse teste a professora Rose é removida da turma 5o Ano A - Super Ensino para
#         verificar se a query traz apenas os dados da turma que o professor atua efetiva-
#         mente.
#         """
#         data_historia = [
#             {
#                 'aluno': self.pedro,
#                 'disciplina': self.historia,
#                 'exercicios_realizados': 10,
#                 'acertos': 2,
#                 'erros': 8,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 2) # 20%
#             },
#             {
#                 'aluno': self.daniel,
#                 'disciplina': self.historia,
#                 'exercicios_realizados': 10,
#                 'acertos': 5,
#                 'erros': 5,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 5) # 50%
#             },
#             {
#                 'aluno': self.maria,
#                 'disciplina': self.historia,
#                 'exercicios_realizados': 10,
#                 'acertos': 8,
#                 'erros': 2,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 8) # 80%
#             },
#         ]
#
#         data_geografia = [
#             {
#                 'aluno': self.pedro,
#                 'disciplina': self.geografia,
#                 'exercicios_realizados': 10,
#                 'acertos': 9,
#                 'erros': 1,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 9) # 90%
#             },
#             {
#                 'aluno': self.daniel,
#                 'disciplina': self.geografia,
#                 'exercicios_realizados': 10,
#                 'acertos': 5,
#                 'erros': 5,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 5) # 50%
#             },
#             {
#                 'aluno': self.maria,
#                 'disciplina': self.geografia,
#                 'exercicios_realizados': 10,
#                 'acertos': 8,
#                 'erros': 2,
#                 'aproveitamento': utils.calculate_aproveitamento(10, 8) # 80%
#             }
#         ]
#
#         # Assegura que estamos iniciando os testes com um log de exercícios zerado.
#         assert (ExercisesDataWharehouse.objects.all().count() == 0)
#
#         total_exercicios_realizados_hist = 0
#         total_acertos_hist = 0
#         total_erros_hist = 0
#         melhor_desempenho_hist = 80 # aluna Maria
#         pior_desempenho_hist = 20 # aluno Pedro
#
#         for d in data_historia:
#             # Simula a resolução de exercícios.
#             self.responder(
#                 d['aluno'], d['disciplina'], d['exercicios_realizados'],
#                 d['acertos'])
#             total_exercicios_realizados_hist += d['exercicios_realizados']
#             total_acertos_hist += d['acertos']
#             total_erros_hist += d['erros']
#
#         indice_turma_hist = utils.calculate_aproveitamento(total_exercicios_realizados_hist, total_acertos_hist)
#
#         total_exercicios_realizados_geo = 0
#         total_acertos_geo = 0
#         total_erros_geo = 0
#         melhor_desempenho_geo = 90 # aluna Maria
#         pior_desempenho_geo = 50 # aluno Pedro
#
#         for d in data_geografia:
#             # Simula a resolução de exercícios.
#             self.responder(
#                 d['aluno'], d['disciplina'], d['exercicios_realizados'],
#                 d['acertos'])
#             total_exercicios_realizados_geo += d['exercicios_realizados']
#             total_acertos_geo += d['acertos']
#             total_erros_geo += d['erros']
#
#         indice_turma_geo = utils.calculate_aproveitamento(total_exercicios_realizados_geo, total_acertos_geo)
#
#         # Remove a professora rose da disciplina de geografia.
#         TurmaDisciplina.objects.get(
#             professor=self.prof_rose,
#             turma=self._5anoA_SuperEnsino,
#             disciplina=self.geografia).delete()
#
#         rs= helpers.consulta_turmas_professor(
#             self.prof_rose, self._5anoA_SuperEnsino.escola)
#
#         self.assertEqual(len(rs), 1, "Query trazendo dados de disciplina que o professor não leciona.")
#
#     def test_query_consulta_desempenho_alunos_turma(self):
#         """Verifica se o desempenho de alunos retorna normalmente."""
#         helpers.query_consulta_desempenho_alunos_turma()
#
#
# class HelperTests2(TestCase, SuperEnsinoDataMixin):
#     """."""
#
#     def setUp(self):
#         """Prepara massa de dados com base no SuperEnsinoDataMixin."""
#         self.setup_data()
#         self.escola = Escola.objects.get(nome='Super Ensino')
#         self.turma_5a = Turma.objects.get(
#             identificador='5a', escola=self.escola)
#         self.matematica = Disciplina.objects.get(
#             nome='Matemática', is_prova_brasil=False)
#
#         self.aluno1 = self.turma_5a.alunos.all()[0]
#         self.aluno2 = self.turma_5a.alunos.all()[1]
#         self.aula_matematica = Aula.objects.filter(
#             disciplina=self.matematica, serie=5, bimestre=1).first()
#
#         # Simula a resolução de exercícios de dois assuntos distintos (cada um
#         # possui 10 questões), onde o índice de acerto no 1o é de 100% e no
#         # segundo 50%.
#         self.responder(self.aluno1, self.matematica, 20, 15)
#         self.responder(self.aluno1, self.matematica, 40, 10)
#
#     def tearDown(self):
#         """."""
#         self._clear_database()
#
#     def test_get_desempenho_de_alunos(self):
#         """."""
#         rs = helpers.get_desempenho_de_alunos(
#             self.turma_5a, self.matematica, 1, 80)
#         # print(rs)
#
#     def test_get_desempenho_disciplinas(self):
#         """Executa something...."""
#
#         rs = ExercisesDataWharehouse.objects.desempenho_turma_alunos_assunto(
#             self.aula_matematica, self.turma_5a, self.matematica, 1)
#         print(rs)
