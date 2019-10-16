"""app.managers.py."""
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q


class HistoricoAulasAssistidasQuerySet(models.query.QuerySet):
    """QuerySet de Visualizações de Aulas."""

    def aluno_views(self, aluno, disciplina, serie, bimestre):
        """Retorna um queryset de visualizações de aulas do aluno.

        O resultado é filtrado por disciplina, serie e bimestre.
        """
        return self.filter(
            aluno=aluno,
            attachment__aula__disciplina=disciplina,
            attachment__aula__serie=serie,
            attachment__aula__bimestre=bimestre)

    def get_aluno(self, pk):
        return self.filter(aluno__pk=pk)

    def is_prova_brasil(self, condition):
        return self.filter(
            aula__disciplina__is_prova_brasil=condition)

    def disciplina(self, disciplina_id):
        return self.filter(
            aula__disciplina__id=disciplina_id)

    def turma(self, turma_id):
        return self.filter(
            aluno__turma__id=turma_id)

    def assunto(self, assunto_id):
        return self.filter(
            aula__id=assunto_id)

    def escola(self, escola):
        return self.filter(aluno__turma__escola=escola)

    def serie(self, serie):
        return self.filter(aula__serie=serie)

    def bimestre(self, bim):
        return self.filter(aula__bimestre=bim)

    def aulas_count(self, serie, disciplina, bimestre=None):
        qs = self.filter(aula__serie=serie, aula__disciplina=disciplina)

        if bimestre is not None:
            qs = qs.filter(aula__bimestre=bimestre)

        return qs.distinct('attachment')

    def count_aulas_by_serie(self, escola, serie, is_prova_brasil):
        """ Retorna o número de aulas assistidas por série """
        return self.filter(
            # aluno__turma__escola = escola,
            aluno__turma__serie=serie,
            aula__disciplina__is_prova_brasil=is_prova_brasil
            ).count()

    def count_aulas_by_turma(self, escola, turma, is_prova_brasil):
        """ Retorna o número de aulas assistidas por turma """
        return self.filter(
            aluno__turma__escola=escola,
            aluno__turma=turma,
            aula__disciplina__is_prova_brasil=is_prova_brasil
            ).count()


class RespostaQuerySet(models.query.QuerySet):
    def select_aluno(self, aluno_id):
        """Seleciona todos os exercícios respondidos pelo aluno."""
        return self.filter(aluno__id=aluno_id)

    def turma(self, turma_id):
        return self.filter(aluno__turma__id=turma_id)

    def turmas(self, turmas):
        """
        Filtra efetivamente apenas as respostas das turmas configuradas no
        sistema. Evitando que ao realizarmos uma pesquisa de desempenho geral
        apareçam series que não existem na escola.
        """

        return self.filter(aluno__turma__in=turmas)

    def is_prova_brasil(self, condition):
        return self.filter(
            exercicio__aula__disciplina__is_prova_brasil=condition)

    def serie(self, serie_id):
        return self.filter(exercicio__aula__serie=serie_id)

    def disciplina(self, disciplina_id):
        return self.filter(exercicio__aula__disciplina__id=disciplina_id)

    def aula(self, aula):
        return self.filter(exercicio__aula=aula)

    def bimestre(self, bimestre_id):
        return self.filter(exercicio__aula__bimestre=bimestre_id)

    def escola(self, escola_id):
        return self.filter(
            aluno__turma__escola__id=escola_id)

    def desempenho(self):
        values = self.values('exercicio__aula__serie').annotate(
             corretas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=True, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             ),
             erradas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=False, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             ),
             total=models.F('corretas') + models.F('erradas'),
             aproveitamento=models.F(
                'corretas')*100/(models.F('corretas') + models.F('erradas'))
            ).order_by('exercicio__aula__serie')

        return values

    def desempenho_aula(self):
        """Retorna o desempenho agrupando os resultados por assunto/aula."""
        values_array = ['exercicio__aula__id', 'exercicio__aula__assunto', 'exercicio__aula__ordem']
        values = self.values(*values_array).annotate(
             corretas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=True, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             ),
             erradas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=False, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             ),
             total=models.F('corretas') + models.F('erradas'),
             aproveitamento=models.F(
                'corretas')*100/(models.F('corretas') + models.F('erradas'))
            ).order_by('exercicio__aula__id', 'exercicio__aula__ordem')

        return values

    def get_desempenho(self, *args):
        """
        Retorna o resulta de erros e acertos de acordo com o agrupamento de atributos passado pelo parâmetro
        *arg. Esse método é semelhante ao desempenho, desempenho_aula dessa classe e outros com a diferênça de
        que os parâmentros de agrupamento pode ser passados livrimente em uma lista. Ex. de uso:

            filters = {'aluno__escola__id':1, 'exercicio__aula__serie':5, 'aluno__serie_atual':5}
            fields = [aluno__escola', 'exercicio__aula__disciplina']
            Resposta.objects.filter(**filters).calc_desempenho(*fields)

        TODO: Refatorar todos os métodos de desempenho para utilizarem get_desempenho como base.

        :param args:
        :return:
        """
        values = self.values(*args).annotate(
            corretas=models.Sum(
                models.Case(
                    models.When(alternativa__correta=True, then=1),
                    default=0, output_field=models.IntegerField()
                )
            ),
            erradas=models.Sum(
                models.Case(
                    models.When(alternativa__correta=False, then=1),
                    default=0, output_field=models.IntegerField()
                )
            ),
            total=models.F('corretas') + models.F('erradas'),
            aproveitamento=models.F(
                'corretas') * 100 / (models.F('corretas') + models.F('erradas'))
        ).order_by('exercicio__aula__id', 'exercicio__aula__ordem')

        return values

    def desempenho_alunos(self):
        """Retorna o desempenho agrupando os resultados por assunto/aula."""
        values = self.values(
            'aluno', 'aluno__nome').annotate(
             corretas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=True, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             ),
             erradas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=False, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             ),
             aproveitamento=models.F(
                'corretas')*100/(models.F('corretas') + models.F('erradas'))
            ).order_by('aproveitamento', 'aluno')

        return values

    def desempenho_disciplinas(self):
        values = self.values(
            'exercicio__aula__disciplina',
            'exercicio__aula__disciplina__nome').annotate(
             corretas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=True, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             ),
             erradas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=False, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             ),
             aproveitamento=models.F(
                'corretas')*100/(models.F('corretas') + models.F('erradas'))
            ).order_by('exercicio__aula__disciplina')

        return values

    def desempenho_serie(self, escola_id, serie, is_prova_brasil=False):
        """Query de desempenho escolar de series."""
        resultset = self.escola(escola_id).filter(
            exercicio__aula__disciplina__is_prova_brasil=is_prova_brasil,
            exercicio__aula__serie=serie).values(
         'exercicio__aula__disciplina',
         'exercicio__aula__disciplina__nome').annotate(
             corretas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=True, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             ),
             erradas=models.Sum(
                 models.Case(
                     models.When(alternativa__correta=False, then=1),
                     default=0, output_field=models.IntegerField()
                 )
             )
         ).order_by('exercicio__aula__disciplina')

        return resultset

    def desempenho_turmas(self, escola_id, serie, is_prova_brasil=False):
        """Dada uma série, retorna o desempenho geral das turmas."""
        return self.escola(escola_id).filter(
            exercicio__aula__serie=serie,
            exercicio__aula__disciplina__is_prova_brasil=is_prova_brasil
            ).values('aluno__turma',
                     'aluno__turma__identificador').annotate(
                corretas=models.Sum(
                    models.Case(
                        models.When(alternativa__correta=True, then=1),
                        default=0, output_field=models.IntegerField()
                        )
                ),
                erradas=models.Sum(
                    models.Case(
                        models.When(alternativa__correta=False, then=1),
                        default=0, output_field=models.IntegerField()
                    )
                ),
                aproveitamento=models.F(
                    'corretas')*100/(
                    models.F('corretas') + models.F('erradas'))
            ).order_by('aluno__turma__serie')


class DisciplinaQuerySet(models.query.QuerySet):
    def total_aulas(self, serie, disciplina, bimestre=None):
        qs = self.filter(serie=serie, disciplina=disciplina)

        if bimestre is not None:
            qs = qs.filter(bimestre=bimestre)

        return qs.count()


class AttachmentQuerySet(models.query.QuerySet):
    def select_aula(self, aula_id):
        return self.filter(aula__serie=aula_id)

    def aulas_count(self, serie, disciplina, bimestre=None):
        qs = self.filter(aula__serie=serie, aula__disciplina=disciplina)

        if bimestre is not None:
            qs = qs.filter(aula__bimestre=bimestre)

        return qs.count()

    def aulas_por_assunto(self, aula_id, bimestre=None):
        q = self.filter(aula__id=aula_id)
        if bimestre:
            q = q.filter(aula__bimestre=bimestre)
        return q

    def disciplina(self, d):
        return self.filter(aula__disciplina__id=d)

    def serie(self, s):
        return self.filter(aula__serie=s)

    def bimestre(self, b):
        return self.filter(aula__bimestre=b)


class ExercicioQuerySet(models.query.QuerySet):
    """."""

    def bimestre_filtered(self, disciplina, serie, bimestre):
        """Retorna o total de exercícios por bimestre.

        A query leva em consideração a disciplina e a série para compor o re-
        sultado final.
        """
        return self.filter(
            aula__disciplina=disciplina,
            aula__serie=serie,
            aula__bimestre=bimestre)

    def serie(self, serie):
        return self.filter(aula__serie=serie)

    def bimestre(self, bimestre):
        return self.filter(aula__bimestre=bimestre)

    def disciplina(self, disciplina):
        return self.filter(aula__disciplina__id=disciplina)

    def is_prova_brasil(self, is_prova_brasil):
        return self.filter(aula__disciplina__is_prova_brasil=is_prova_brasil)

    def assunto(self, assunto_id):
        return self.filter(aula__id=assunto_id)


class AlunoQuerySet(models.query.QuerySet):
    def filter_escola_slug(self, slug):
        return self.filter(escola__slug=slug)

    def search_by_name(self, term):
        return self.filter(nome__unaccent__icontains=term)

    def count_alunos_by_turma(self, escola, turma):
        """ Conta o número total de alunos de uma turma """
        return self.filter(turma=turma).count()

    def count_alunos_by_serie(self, escola, serie):
        """ Conta o número total de alunos de uma série """
        return self.filter(
            turma__escola=escola).filter(turma__serie=serie).count()

    def turma(self, turma):
        return self.filter(turma=turma)

    def desempenho_aluno(self, is_prova_brasil=False):
        return self.values('nome').annotate(
            corretas=models.Sum(
                models.Case(
                    models.When(
                        Q(resposta__alternativa__correta=True) &
                        Q(resposta__exercicio__aula__disciplina__is_prova_brasil=is_prova_brasil), then=1),
                    default=0, output_field=models.IntegerField()
                )
            ),
            erradas=models.Sum(
                models.Case(
                    models.When(
                        Q(resposta__alternativa__correta=False) &
                        Q(resposta__exercicio__aula__disciplina__is_prova_brasil=is_prova_brasil), then=1),
                    default=0, output_field=models.IntegerField()
                )
            ),
        )


class EscolaQuerySet(models.query.QuerySet):
    def get_active_schools (self, user):
        """Based on the user profile, return the list of schools avaliable."""
        from app.models import Profile

        try:
            if user.is_superuser:
                return self.order_by('nome')

            profile = Profile.objects.get(user=user)

            if profile.role == Profile.GESTOR_ESCOLAR:
                from app.models import Gestor

                gestor = Gestor.objects.filter(user=user)
                return self.filter(gestor=gestor)
            elif profile.role == Profile.PROFESSOR:
                from app.models import Professor

                professor = Professor.objects.get(user=user)
                return professor.escola.all()
            else:
                return None
        except ObjectDoesNotExist:
            return None

    def search_by_name(self, term):
        return self.filter(nome__unaccent__icontains=term)

    def from_slug (self, slug):
        return self.get(slug=slug)


class ResponsavelQuerySet(models.query.QuerySet):
    def filter_escola_slug(self, slug):
        return self.filter(escola__slug=slug)

    def search_by_name(self, term):
        return self.filter(nome__unaccent__icontains=term)


class TurmaQuerySet(models.query.QuerySet):
    def escola(self, escola):
        return self.filter(escola=escola).order_by('serie')


class ProfessorQuerySet(models.query.QuerySet):
    def filter_escola_slug(self, slug):
        return self.filter(escola__slug=slug)

    def search_by_name(self, term):
        return self.filter(nome__unaccent__icontains=term)

    def get_escolas(self, user):
        return self.get(user=user).escola.all()


class GestorQuerySet(models.query.QuerySet):
    def get_escolas(self):
        return self.escola.all()
