from django.test import TestCase
from app.models import Escola
from app.models import Turma
from app.models import Aluno
from app.models import Profile
from app.models import Professor
from app.models import Responsavel
from app.setups import create_aluno_ex
from app.setups import create_responsavel
from app.setups import create_professor
from app.setups import create_escola_super_ensino
from datetime import date
from app.setups import parse_data
from app.setups import parse_professor_data
from datetime import datetime
from app import setups
from django.contrib.auth import get_user_model


class SetupTests(TestCase):
    def setUp(self):
        self.data = [
            {
                'nome': 'ANA FLAVIA SARAIVA DE OLIVEIRA',
                'matricula': '1683559-0',
                'nascimento': '30/08/2006',
                'username': 'ana.oliveira',
                'genero': Profile.FEMININO,
                'mae': {
                        'nome': 'ALICE SARAIVA MEDEIROS',
                        'username': 'alice.medeiros'
                    },
                'pai': {
                        'nome': 'FABIO CESAR OLIVEIRA FILHO',
                        'username': 'fabio.filho'
                    }
            }
        ]
        self.data_without_pai = [
            {
                'nome': 'ANA FLAVIA SARAIVA DE OLIVEIRA',
                'matricula': '1683559-0',
                'nascimento': '30/08/2006',
                'username': 'ana.oliveira',
                'genero': Profile.FEMININO,
                'mae': {
                        'nome': 'ALICE SARAIVA MEDEIROS',
                        'username': 'alice.medeiros'
                    },
                'pai': None
            }
        ]

        self.data_professores = [
            {
                'nome': 'ANA CASSIA NASCIMENTO ROSAS',
                'matricula': '98.105918-1A',
                'funcao': 'PROFESSOR 1º AO 5º ANO',
                'username': 'ana.rosas'
            }]

        self.escola = Escola(nome='Escola Padrão')
        self.escola.save()

        self.turma = Turma(
            identificador='T0001',
            descricao='T0001_descr',
            status=1,
            escola=self.escola,
            serie=5
        )
        self.turma.save()

    def tearDown(self):
        Escola.objects.all().delete()
        Responsavel.objects.all().delete()
        Aluno.objects.all().delete()
        Professor.objects.all().delete()
        get_user_model().objects.all().delete()
        Turma.objects.all().delete()

    def test_create_responsavel(self):
        nome = 'Responsavel'
        username = 'responsavel'
        resp = create_responsavel(nome, username)

        self.assertEqual(resp.role, Profile.RESPOSIBLE)
        self.assertEqual(resp.nome, nome)
        self.assertEqual(resp.user.username, username)

    def test_create_aluno_ex(self):
        nome = 'FULANO DE TAL'
        username = 'fulaninho'
        matricula = '12345'
        birthday = date(2008, 9, 1)
        pai = create_responsavel('PAI', 'pai')
        mae = create_responsavel('MAE', 'mae')

        aluno = create_aluno_ex(
            self.turma, nome, username,
            Profile.MASCULINO, birthday, matricula, mae, pai)

        self.assertEqual(aluno.role, Profile.STUDENT)
        self.assertEqual(aluno.nome, nome)
        self.assertEqual(aluno.user.username, username)
        self.assertEqual(aluno.genero, Profile.MASCULINO)
        self.assertEqual(aluno.data_nascimento, birthday)
        self.assertEqual(aluno.matricula, matricula)
        self.assertEqual(aluno.responsaveis.all().count(), 2)

    def test_parse_data(self):
        parse_data(self.turma, self.data)
        aluno = Aluno.objects.all().first()

        self.assertEqual(aluno.role, Profile.STUDENT)
        self.assertEqual(aluno.nome, 'ANA FLAVIA SARAIVA DE OLIVEIRA')
        self.assertEqual(aluno.user.username, 'ana.oliveira')
        self.assertEqual(aluno.genero, Profile.FEMININO)
        self.assertEqual(
            aluno.data_nascimento,
            datetime.strptime('30/08/2006', '%d/%m/%Y').date())
        self.assertEqual(aluno.matricula, '1683559-0')
        self.assertEqual(aluno.responsaveis.all().count(), 2)

    def test_parse_data_sem_pai(self):
        parse_data(self.turma, self.data_without_pai)
        aluno = Aluno.objects.all().first()

        self.assertEqual(aluno.role, Profile.STUDENT)
        self.assertEqual(aluno.nome, 'ANA FLAVIA SARAIVA DE OLIVEIRA')
        self.assertEqual(aluno.user.username, 'ana.oliveira')
        self.assertEqual(aluno.genero, Profile.FEMININO)
        self.assertEqual(
            aluno.data_nascimento,
            datetime.strptime('30/08/2006', '%d/%m/%Y').date())
        self.assertEqual(aluno.matricula, '1683559-0')
        self.assertEqual(aluno.responsaveis.all().count(), 1)

    def test_parse_full_data(self):
        parse_data(self.turma, setups.data)

        self.assertEqual(Aluno.objects.all().count(), 30)
        self.assertEqual(Responsavel.objects.all().count(), 56)

    def test_create_professor(self):
        nome = 'professor'
        username = 'prof'
        matricula = '1qwe3'
        funcao = 'bombril'

        professor = create_professor(
            self.escola, nome, username, matricula, funcao)

        self.assertEqual(professor.role, Profile.PROFESSOR)
        self.assertEqual(professor.nome, nome)
        self.assertEqual(professor.user.username, username)
        self.assertEqual(professor.matricula, matricula)
        self.assertEqual(professor.funcao, funcao)

    def test_parse_professor_data(self):
        parse_professor_data(self.escola, setups.data_professores)

    def test_create_super_ensino(self):
        create_escola_super_ensino()
