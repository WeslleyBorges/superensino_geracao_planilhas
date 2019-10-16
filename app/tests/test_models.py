from django.test import TestCase
from app.models import Resposta, UserSchoolRelationshipManager, Tag
from model_mommy import mommy
from django.contrib.auth import get_user_model
from app.models import Alternativa
from app.models import Exercicio
from app.models import Aluno, Profile, Professor, TurmaDisciplina, Escola
from app.models import (Disciplina, Aula, Turma)
from django.db import models
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from core.tests import AppModelTestMixing
from django.db import transaction


class RespostaTests(TestCase):
    def setUp(self):
        self.exercicio = mommy.make('app.Exercicio')
        self.aluno = mommy.make('app.Aluno')
        self.alternativas = mommy.make(
            'app.Alternativa',
            _quantity=4,
            exercicio=self.exercicio,
            correta=False)

    def tearDown(self):
        get_user_model().objects.all().delete()
        Resposta.objects.all().delete()
        Alternativa.objects.all().delete()
        Exercicio.objects.all().delete()

    def test_apply_response(self):
        resposta = Resposta.aplicar_resposta(
            self.aluno, self.exercicio, self.alternativas[0])

        reposta_id = resposta.id

        resposta = Resposta.aplicar_resposta(
            self.aluno, self.exercicio, self.alternativas[1])
        current = Resposta.objects.get(pk=reposta_id)

        self.assertEqual(current.alternativa, self.alternativas[0])


class RelatorioDesempenhoTest(TestCase):
    def setUp(self):
        self.disciplina = mommy.make('app.Disciplina', is_prova_brasil=False)
        self.aula = mommy.make('app.Aula', disciplina=self.disciplina)
        self.aluno = mommy.make('app.Aluno', _quantity=10)
        self.exercicio = mommy.make('app.Exercicio', aula=self.aula)
        self.alternativas = mommy.make(
            'app.Alternativa',
            _quantity=4,
            exercicio=self.exercicio,
            correta=False)

        self.alternativas[0].correta = True
        self.alternativas[0].save()

    def tearDown(self):
        get_user_model().objects.all().delete()
        Alternativa.objects.all().delete()
        Exercicio.objects.all().delete()

    def test_console(self):
        q = Aluno.objects.all().desempenho_aluno()


class AlunoQuerySetTest(TestCase):
    def setUp(self):
        d_prova_brasil = mommy.make('app.Disciplina', is_prova_brasil=True)
        d_super_reforco = mommy.make('app.Disciplina', is_prova_brasil=False)

        self.aula_pb = mommy.make('app.Aula', disciplina=d_prova_brasil)
        self.aula_sr = mommy.make('app.Aula', disciplina=d_super_reforco)

        self.turma1 = mommy.make('app.Turma')
        self.alunos1 = mommy.make('app.Aluno', _quantity=3)
        self.turma1.alunos.add(*self.alunos1)
        self.turma1.save()

        self.turma2 = mommy.make('app.Turma')
        self.alunos2 = mommy.make('app.Aluno', _quantity=5)
        self.turma2.alunos.add(*self.alunos2)
        self.turma2.save()

        # Exercicios super reforço
        for i in range(0, 3):
            exercicio = mommy.make('app.Exercicio', aula=self.aula_sr)
            alternativas = mommy.make(
                'app.Alternativa',
                _quantity=4,
                exercicio=exercicio,
                correta=False)

            alternativas[0].correta = True
            alternativas[0].save()

        # Exercícios prova brasil
        for i in range(0, 2):
            exercicio = mommy.make('app.Exercicio', aula=self.aula_pb)
            alternativas = mommy.make(
                'app.Alternativa',
                _quantity=4,
                exercicio=exercicio,
                correta=False)

            alternativas[0].correta = True
            alternativas[0].save()

        # Resposta super ensino
        self.responder_exercicios(Exercicio.objects.filter(
            aula__disciplina__is_prova_brasil=False).order_by('id'))

        # Respostas prova brasil
        self.responder_exercicios(Exercicio.objects.filter(
            aula__disciplina__is_prova_brasil=True).order_by('id'))

    def responder_exercicios(self, exercicios):
        alunos = Aluno.objects.all()
        for aluno in alunos:
            i = 0
            for ex in exercicios:
                resposta = 1
                if i % 2 == 0:
                    resposta = 0

                alternativas = Alternativa.objects.filter(exercicio=ex)
                Resposta.aplicar_resposta(
                    aluno, ex, alternativas[resposta])
                i += 1

    def tearDown(self):
        get_user_model().objects.all().delete()
        Alternativa.objects.all().delete()
        Exercicio.objects.all().delete()
        Disciplina.objects.all().delete()
        Aula.objects.all().delete()
        Turma.objects.all().delete()

    def test_filtra_turma(self):
        qs = Aluno.objects.turma(self.turma1)
        self.assertEqual(qs.count(), 3)

    def test_desempenho_super_reforco(self):
        q = Aluno.objects.turma(self.turma1).desempenho_aluno()

        self.assertEqual(q[0]['corretas'], 2)
        self.assertEqual(q[0]['erradas'], 1)
        self.assertEqual(q[1]['corretas'], 2)
        self.assertEqual(q[1]['erradas'], 1)
        self.assertEqual(q[2]['corretas'], 2)
        self.assertEqual(q[2]['erradas'], 1)

    def test_desempenho_prova_brasil(self):
        q = Aluno.objects.turma(self.turma1).desempenho_aluno(True)

        self.assertEqual(q[0]['corretas'], 1)
        self.assertEqual(q[0]['erradas'], 1)
        self.assertEqual(q[1]['corretas'], 1)
        self.assertEqual(q[1]['erradas'], 1)
        self.assertEqual(q[2]['corretas'], 1)
        self.assertEqual(q[2]['erradas'], 1)

    def test_desempenho_super_reforco_sem_respostas(self):
        Resposta.objects.all().delete()
        q = Aluno.objects.turma(self.turma1).desempenho_aluno()

        self.assertEqual(q.count(), 3)

        self.assertEqual(q[0]['corretas'], 0)
        self.assertEqual(q[0]['erradas'], 0)
        self.assertEqual(q[1]['corretas'], 0)
        self.assertEqual(q[1]['erradas'], 0)
        self.assertEqual(q[2]['corretas'], 0)
        self.assertEqual(q[2]['erradas'], 0)

    def test_desempenho_prova_brasil_sem_respostas(self):
        Resposta.objects.all().delete()
        q = Aluno.objects.turma(self.turma1).desempenho_aluno(True)

        self.assertEqual(q.count(), 3)

        self.assertEqual(q[0]['corretas'], 0)
        self.assertEqual(q[0]['erradas'], 0)
        self.assertEqual(q[1]['corretas'], 0)
        self.assertEqual(q[1]['erradas'], 0)
        self.assertEqual(q[2]['corretas'], 0)
        self.assertEqual(q[2]['erradas'], 0)


class ProfileCreateTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make(get_user_model())

    def tearDown(self):
        get_user_model().objects.all().delete()

    def test_create_administrador(self):
        new_profile = mommy.make('app.Administrador', user=self.user)
        new_profile.save()
        self.assertEqual(Profile.ADMINISTRATOR, new_profile.role)

    def test_create_gestor(self):
        new_profile = mommy.make('app.Gestor', user=self.user)
        new_profile.save()
        self.assertEqual(Profile.GESTOR_ESCOLAR, new_profile.role)

    def test_create_aluno(self):
        new_profile = mommy.make('app.Aluno', user=self.user)
        new_profile.save()
        self.assertEqual(Profile.STUDENT, new_profile.role)

    def test_create_responsavel(self):
        new_profile = mommy.make('app.Responsavel', user=self.user)
        new_profile.save()
        self.assertEqual(Profile.RESPOSIBLE, new_profile.role)

    def test_create_professor(self):
        new_profile = mommy.make('app.Professor', user=self.user)
        new_profile.save()
        self.assertEqual(Profile.PROFESSOR, new_profile.role)


class EscolaTestCase(TestCase):
    """TestCases de escola."""

    def setUp(self):
        """Configuração inicial de testes."""
        self.escola_full = mommy.make('app.Escola')
        mommy.make('app.Aluno', escola=self.escola_full, _quantity=10)

        self.escola_empty = mommy.make('app.Escola')

    def tearDown(self):
        """Finalização de testes."""
        with transaction.atomic():
            self.escola_full.delete()
            self.escola_empty.delete()

    def test_assure_slug_unique(self):
        """Test de slug único.

        Verifica se o slug da escola é realmente único. Como temos um signal
        gerando os slugs automaticamente, a maneira que temos de testar esse
        comportamento é gerando as escolas e posteriormente tentar atribuir o
        slug de uma a outra.
        """
        escola_a = mommy.make('app.Escola')
        escola_b = mommy.make('app.Escola')

        try:
            # Duplicates should be prevented
            with transaction.atomic():
                escola_b.slug = escola_a.slug
                escola_b.save()
                self.fail('Duplicated Slug allowed')
        except IntegrityError:
            pass


    def test_get_alunos_count_with_alunos(self):
        """Checa o comportamento do método com N alunos."""
        self.assertEqual(10, self.escola_full.get_alunos_count())

    def test_get_alunos_count_without_alunos(self):
        """Verifica o método para uma escola que não tem alunos cadastrados."""
        self.assertEqual(0, self.escola_empty.get_alunos_count())


class ProfessorModelTest(TestCase, AppModelTestMixing):
    def setUp(self):
        self.setup_data()

    def tearDown(self):
        self.teardown_data()

    def test_turmas_professor(self):
        # Em quais turmas Joe leciona?
        joes_turmas = Turma.objects.filter(turmas=self.joe).distinct()
        self.assertEqual(list(joes_turmas), [self._5anoA, self._5anoB])

    def test_turmas_disciplina_professor(self):
        self.assertEqual(self.joe.grade_curricular.all().count(), 3)

    def test_retorna_escolas_do_professor(self):
        """
        Checa pelo número de escolas retornadas e o método está tranzendo as escolas
        que foram configuradas para o professor Joe no setUp
        """
        escolas = self.joe.get_escolas_json()
        self.assertEqual(len(escolas), 3)

class GestorModelTestCase(TestCase, AppModelTestMixing):
    def setUp(self):
        self.setup_data()

    def tearDown(self):
        self.teardown_data()

    def test_retorna_escolas_do_gestor(self):
        escolas = self.gestor.get_escolas_json()
        self.assertEqual(len(escolas), 4)

    def test_retorna_escolas_do_gestor_excluido_uma_escola(self):
        self.escola_balbina_mestrinho.delete()

        escolas = self.gestor.get_escolas_json()
        self.assertEqual(len(escolas), 3)


# class UserSchoolRelationshipManagerTest(TestCase):
#     def setUp(self):
#         self.tag_semed = Tag.objects.create(name='semed')
#
#         self.master = mommy.make(get_user_model())
#         self.acessor = mommy.make(get_user_model())
#         self.ddz = mommy.make(get_user_model())
#
#         self.hogwarts = Escola.objects.create(nome="Hogwarts")
#         self.hogwarts.tags.add(self.tag_semed)
#         self.hogwarts.save()
#
#         self.avalon = Escola.objects.create(nome="Avalon")
#         self.hogwarts.tags.add(self.tag_semed)
#         self.hogwarts.save()
#
#         self.cobra_kai = Escola.objects.create(nome="Cobra Kai")
#
#     def test_dont_duplicate_mappint(self):
#         assert UserSchoolRelationshipManager.objects.all().count() == 0
#         mngr = UserSchoolRelationshipManager.associate_master(self.master, self.hogwarts)
#         self.assertEqual(mngr.role, UserSchoolRelationshipManager.MASTER)
#
#     def test_associate_master(self):
#         mngr = UserSchoolRelationshipManager.associate_master(self.master, self.hogwarts)
#         self.assertEqual(mngr.role, UserSchoolRelationshipManager.MASTER)
#
#     def test_associate_assessor(self):
#         mngr = UserSchoolRelationshipManager.associate_assessor(self.master, self.hogwarts)
#         self.assertEqual(mngr.role, UserSchoolRelationshipManager.ASSESSOR)
#
#     def test_associate_ddz(self):
#         mngr = UserSchoolRelationshipManager.associate_ddz(self.master, self.hogwarts)
#         self.assertEqual(mngr.role, UserSchoolRelationshipManager.DDZ)
#
#     def test_associate_by_tag(self):
#         UserSchoolRelationshipManager.associate_by_tag(
#             self.master, self.tag_semed, UserSchoolRelationshipManager.MASTER)
