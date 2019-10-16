from core.tests import SuperEnsinoDataMixin
from django.test import TestCase
from app.models import Escola
from app.models import Turma
from app import services


class RespostaTests(TestCase, SuperEnsinoDataMixin):
    def setUp(self):
        self.setup_data()

        self.superensino = Escola.objects.get(nome='Super Ensino')
        self.turma5a_superensino = Turma.objects.get(escola=self.superensino, identificador='5a')
        self.aluno_super_1 = self.turma5a_superensino.alunos.all()[0]

        # Configuração de resposta para a validação das estatísticas
        # A1 => [10, 10]; A2 => [0, 10]
        self.responder(self.aluno_super_1, self.disc_matematica, 20, 10)

    def test_get_desempenho_individual_por_disciplina(self):
        """Calcula o desempenho da 5a série da escola super ensino."""
        result = services.get_desempenho_individual_por_disciplina(
            self.aluno_super_1, self.disc_matematica, 5, None, True)

        print(result)
