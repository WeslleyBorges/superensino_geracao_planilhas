from django.db import models
from app.models import Escola
from app.models import Turma
from app.models import Exercicio, Disciplina
from app.models import Aluno
from app.models import Alternativa
from .managers import ExerciciosDataWharehouseQuerySet


class ExercisesDataWharehouse(models.Model):
    """
    Armazena dados detalhados e desnormalizados do histórico de respostas dos
    alunos. A desnormalização visa facilitar a realização de queries para rela-
    tórios requeridos pelo projeto.
    """
    escola = models.ForeignKey(Escola)
    turma = models.ForeignKey(Turma)
    serie = models.IntegerField()
    bimestre = models.IntegerField()
    aluno = models.ForeignKey(Aluno)
    exercicio = models.ForeignKey(Exercicio)
    disciplina = models.ForeignKey(Disciplina)
    is_prova_brasil = models.BooleanField()
    resposta = models.ForeignKey(Alternativa, related_name='respaluno')  # resposta do aluno
    gabarito = models.ForeignKey(Alternativa, related_name='gabarito')  # resposta correta

    objects = ExerciciosDataWharehouseQuerySet.as_manager()

    @classmethod
    def add(cls, aluno, exercicio, resposta):
        """
        O método add recebe apenas parâmetros suficientes para extrair as
        informações de wharehouse dos exercícios.
        """
        resp_found = ExercisesDataWharehouse.objects.filter(
            escola=aluno.escola,
            aluno=aluno,
            exercicio=exercicio
        ).exists()

        if not resp_found:
            data = cls(
                escola=aluno.escola,
                aluno = aluno,
                turma = aluno.turma_atual(),
                serie = exercicio.aula.serie,
                bimestre = exercicio.aula.bimestre,
                exercicio = exercicio,
                disciplina = exercicio.aula.disciplina,
                is_prova_brasil = exercicio.aula.disciplina.is_prova_brasil,
                resposta = resposta,
                gabarito = exercicio.alternativa_correta()
            )

            data.save()
            return data

class DesempenhoTurmaWharehouse(models.Model):
    """
    Classe de processamento

    Armazenas os índices de desempenho mínimos e máximos da turma. Essa é entidade
    global ao sistema, armazenado os principais índices de todas as turmas. Sua
    atualização não deve estar associadas a chamadas diretas de views ou outros
    models. Como se trata de um processamento considerável, essa entidade deve ser
    atualizada periodicamente (12h/12h, 24h/24/ 15d/15d, etc..) ou em um cenário
    ideal rodar em um microserviço totalmente separado.
    """

    turma = models.ForeignKey(Turma)
    menorDesempenho = models.IntegerField()
    maiorDesempenho = models.IntegerField()

    @classmethod
    def update_indices_turmas(self):
        """
        Dispara o método de atualização dos índices máximos e mínimos de turma__serie
        """
        pass
