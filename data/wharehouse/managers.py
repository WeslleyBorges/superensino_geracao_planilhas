"""managers.py."""
from django.db import models
from django.db.models import F


class ExerciciosDataWharehouseQuerySet(models.query.QuerySet):
    """."""

    def get_desempenho_individual_disciplina(
            self, aluno, turma, disciplina, bimestre):
        """Retorna queryset com os dados de desempenho do aluno na disciplina.

        Retorna um queryset agrupando os dados por Nome da Escola, Nome do
        Aluno Código da Turma e Assunto. Onde para cada linha do resultado é
        calculado o número de acertos, erros, total de exercícios e índice de
        aproveitamento.
        """
        return self.filter(
            disciplina=disciplina,
            turma=turma,
            aluno=aluno,
            exercicio__aula__bimestre=bimestre).values(
            'escola__nome',
            'aluno',
            'aluno__nome',
            'turma__identificador',
            'exercicio__aula__assunto'
        ).annotate(
            acertos=models.Sum(
                models.Case(
                    models.When(resposta=F('gabarito'), then=1), default=0,
                    output_field=models.IntegerField()
                )
            ),
            ttl_exercicios=models.Count('exercicio'),
            erros=F('ttl_exercicios') - F('acertos'),
            indice=F('acertos') * 100 / F('ttl_exercicios')
        )

    def get_desempenho_de_alunos_por_disciplina(
            self, disciplina, turma, bimestre):
        """Desempenho de alunos por disciplina.

        O resultado é filtrado por disciplina, turma e bimestre.
        """
        return self.filter(
            disciplina=disciplina,
            turma=turma,
            exercicio__aula__bimestre=bimestre).values(
            'aluno',
            'aluno__nome',
            'turma__identificador',
            'disciplina__nome'
        ).annotate(
            acertos=models.Sum(
                models.Case(
                    models.When(resposta=F('gabarito'), then=1), default=0,
                    output_field=models.IntegerField()
                )
            ),
            ttl_exercicios=models.Count('exercicio'),
            erros=F('ttl_exercicios') - F('acertos'),
            indice=F('acertos') * 100 / F('ttl_exercicios')
        )

    def desempenho_turma_alunos_assunto(
            self, aula, turma, disciplina, bimestre):
        """Desempenho de alunos por disciplina.

        O resultado é filtrado por disciplina, turma e bimestre.
        """
        return self.filter(
            exercicio__aula=aula,
            disciplina=disciplina,
            turma=turma,
            exercicio__aula__bimestre=bimestre).values(
            'aluno',
            'turma__identificador',
            'exercicio__aula'
        ).annotate(
            acertos=models.Sum(
                models.Case(
                    models.When(resposta=F('gabarito'), then=1), default=0,
                    output_field=models.IntegerField()
                )
            ),
            ttl_exercicios=models.Count('exercicio'),
            erros=F('ttl_exercicios') - F('acertos'),
            indice=F('acertos') * 100 / F('ttl_exercicios')
        )

    def desempenho_turma_assuntos(
            self, disciplina, turma, bimestre):
        """Desempenho de alunos por disciplina.

        O resultado é filtrado por disciplina, turma e bimestre.
        """
        return self.filter(
            disciplina=disciplina,
            turma=turma,
            exercicio__aula__bimestre=bimestre).values(
            'turma__identificador',
            'disciplina__nome',
            'disciplina',
            'exercicio__aula__assunto',
            'exercicio__aula'
        ).annotate(
            acertos=models.Sum(
                models.Case(
                    models.When(resposta=F('gabarito'), then=1), default=0,
                    output_field=models.IntegerField()
                )
            ),
            ttl_exercicios=models.Count('exercicio'),
            erros=F('ttl_exercicios') - F('acertos'),
            indice=F('acertos') * 100 / F('ttl_exercicios')
        )

    def desempenho_alunos_assuntos(
            self, disciplina, turma, aluno, bimestre):
        """Desempenho de alunos por disciplina.

        O resultado é filtrado por disciplina, turma e bimestre.
        """
        return self.filter(
            disciplina=disciplina,
            turma=turma,
            aluno=aluno,
            exercicio__aula__bimestre=bimestre).values(
            'turma__identificador',
            'disciplina__nome',
            'disciplina',
            'exercicio__aula__assunto',
            'exercicio__aula'
        ).annotate(
            acertos=models.Sum(
                models.Case(
                    models.When(resposta=F('gabarito'), then=1), default=0,
                    output_field=models.IntegerField()
                )
            ),
            ttl_exercicios=models.Count('exercicio'),
            erros=F('ttl_exercicios') - F('acertos'),
            indice=F('acertos') * 100 / F('ttl_exercicios'))

    def turmas(self, turmas):
        return self.filter(turma__in=turmas)

    def disciplinas(self, disciplinas):
        """
        Disciplinas aceita um queryset ou um dictionary como parâmetro.
        """
        return self.filter(disciplina__in=disciplinas)

    def get_desempenho_turmas_professor(self, professor, escola):
        """
        Retorna o desempenho de turmas do professor, agrupando todas as
        escolas que ele atua.
        """

        disciplinas = professor.get_disciplinas_ids()
        rs = self.filter(
            escola = escola,
            turma__turmas=professor,
            disciplina__in= disciplinas).values(
                'turma',
                'disciplina',
                'turma__serie',
                'turma__identificador',
                'escola__nome', 'disciplina__nome').annotate(
                    correta=models.Sum(
                        models.Case(
                            models.When(resposta=F('gabarito'), then=1), default=0,
                            output_field=models.IntegerField()
                        )
                    ),
                    exercicios_realizados = models.Count('exercicio'),
                    indice = F('correta') * 100 / F('exercicios_realizados')
                ).order_by('turma__identificador')

        return rs

    def get_melhor_desempenho_disciplina_turma(self, disciplina, turma):
        """
        Retorna no melhor desempenho da turma.
        """
        return self.filter(
            disciplina=disciplina, turma=turma).values(
            'escola__nome',
            'aluno__nome',
            'turma__identificador',
            'disciplina__nome'
        ).annotate(
            correta=models.Sum(
                models.Case(
                    models.When(resposta=F('gabarito'), then=1), default=0,
                    output_field=models.IntegerField()
                )
            ),
            exercicios_realizados = models.Count('exercicio'),
            indice = F('correta') * 100 / F('exercicios_realizados')
        ).aggregate(max=models.Max(F('indice')))['max']

    def get_pior_desempenho_disciplina_turma(self, disciplina, turma):
        """
        Retorna o pior desempenho da turma.
        """
        return self.filter(
            disciplina=disciplina, turma=turma).values(
            'escola__nome',
            'aluno__nome',
            'turma__identificador',
            'disciplina__nome'
        ).annotate(
            correta=models.Sum(
                models.Case(
                    models.When(resposta=F('gabarito'), then=1), default=0,
                    output_field=models.IntegerField()
                )
            ),
            exercicios_realizados = models.Count('exercicio'),
            indice = F('correta') * 100 / F('exercicios_realizados')
        ).aggregate(min=models.Min(F('indice')))['min']

    def get_desempenho_turma_disciplina_details(
            self, turma, disciplina, bim=1):
        """Retorna o desempenho da turma.

        Caso a turma não tenha dados suficientes para calcular o desempenho
        None é retornado.
        """
        queryset = self.filter(
            disciplina=disciplina,
            turma=turma,
            exercicio__aula__bimestre=bim).values(
            'escola__nome',
            'turma__identificador',
            'disciplina__nome'
        ).annotate(
            correta=models.Sum(
                models.Case(
                    models.When(resposta=F('gabarito'), then=1), default=0,
                    output_field=models.IntegerField()
                )
            ),
            exercicios_realizados=models.Count('exercicio'),
            indice=F('correta') * 100 / F('exercicios_realizados')
        )

        if len(queryset) > 0:
            data = {
                'ttl_alunos': turma.alunos.count(),
                'indice_turma': queryset[0]['indice'],
                'exercicios_realizados': queryset[0]['exercicios_realizados'],
                'erros': queryset[0]['exercicios_realizados'] -
                queryset[0]['correta'],
                'acertos': queryset[0]['correta'],
                'videos_assistidos': 0,
                'indice_geral': 0,
                'max': self.get_melhor_desempenho_disciplina_turma(
                    disciplina, turma),
                'min': self.get_pior_desempenho_disciplina_turma(
                    disciplina, turma),
                'ranking': 0
            }

            return data
        else:
            return None

    def get_exercicios_respondidos_escola(self, escola):
        """
        Retorna a quantidade de exercícios respondidos por uma determinada escola
        :param escola:
        :return:

        """
        return self.filter(escola=escola)

    def is_prova_brasil(self, is_prova_brasil):
        return self.filter(is_prova_brasil=is_prova_brasil)

    def disciplinas(self, disciplinas):
        return self.filter(disciplina__in=disciplinas)

    def series(self, series):
        return self.filter(serie__in=series)