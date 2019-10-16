from django.db.models import Sum, Case, When, F, Count, IntegerField

from app.models import Aluno, Profile, Gestor, Professor
from data.wharehouse.models import ExercisesDataWharehouse
from api.middleware import get_current_user


def base_get_desempenho(*columns, **filters):
    """
    Query com base na entidade ExercicesDataWharehouse. Para consulta de desempenho agrupados
    por escola, serie, turma, disciplina e aula.
    """
    queryset = ExercisesDataWharehouse.objects.filter(**filters).values(*columns).annotate(
        acertos=Sum(
            Case(
                When(resposta=F('gabarito'), then=1), default=0,
                output_field=IntegerField()
            )
        ),
        ttl_exercicios=Count('exercicio'),
        indice=F('acertos') * 100 / F('ttl_exercicios')
    )

    return queryset


def base_get_desempenho_alunos(*columns, **filters):
    """
    Query com base no Aluno. Traz resultados de desempenho vazio para os alunos
    que não resolveram nenhum exercicio. Os campos e filtros são passados com
    base na class exercicesdatawharehouse__.

    Ex: Filtra todos os exercicios de reforço da turma 1

    columns = {'id', 'nome', 'acertos', 'ttl_exercicios', 'indice'}
    filters = {
        'turma': turma
    }
    """
    query = Aluno.objects.filter(**filters).annotate(
        acertos=Sum(
            Case(
                When(exercisesdatawharehouse__resposta=F('exercisesdatawharehouse__gabarito'), then=1), default=0,
                output_field=IntegerField())),
        ttl_exercicios=Count('exercisesdatawharehouse__exercicio'),
        indice=Case(When(ttl_exercicios=0, then=0), default=F('acertos') * 100 / F('ttl_exercicios'))
        ).values(*columns)

    return query


def get_desempenho_series(escola, prova_brasil, serie=None):
    columns = {'escola', 'serie'}
    filters = {
        'escola': escola,
        'is_prova_brasil': prova_brasil
    }

    if serie:
        filters['serie'] = serie

    return base_get_desempenho(*columns, **filters).order_by('serie')


def get_desempenho_disciplinas_filtrado_por_serie(escola, serie, prova_brasil):
    columns = {'disciplina', 'disciplina__nome'}
    filters = {
        'escola': escola,
        'serie': serie,
        'is_prova_brasil': prova_brasil
    }

    return base_get_desempenho(*columns, **filters).order_by('indice')


def get_desempenho_assuntos_filtrado_por_disciplina(
        escola, disciplina, serie=None, turma=None, prova_brasil=None):
    columns = {
        'exercicio__aula',
        'exercicio__aula__assunto',
        'exercicio__aula__ordem'
    }
    filters = {
        'escola': escola,
        'disciplina': disciplina,
        'serie': serie
    }

    if turma:
        filters['turma'] = turma

    if prova_brasil:
        filters['is_prova_brasil'] = prova_brasil

    return base_get_desempenho(*columns, **filters).order_by('indice')


def get_desempenho_turmas_filtrado_por_serie(turma, escola, serie, prova_brasil):
    columns = {'turma', 'turma__identificador'}
    filters = {
        'turma': turma,
        'escola': escola,
        'serie': serie,
        'is_prova_brasil': prova_brasil
    }
    return base_get_desempenho(*columns, **filters).order_by('turma')


def get_desempenho_disciplinas_filtrado_por_turma(escola, turma, prova_brasil):
    columns = {
        'disciplina',
        'disciplina__nome'
    }
    filters = {
        'escola': escola,
        'turma': turma,
        'serie': turma.serie,
        'is_prova_brasil': prova_brasil
    }
    return base_get_desempenho(*columns, **filters).order_by('indice')


def get_desempenho_assuntos_filtrado_por_disciplina_e_turma(escola, disciplina, turma):
    columns = {
        'exercicio__aula',
        'exercicio__aula__nome',
        'exercicio__aula__ordem'
    }
    filters = {
        'escola': escola,
        'disciplina': disciplina,
        'turma': turma,
        'serie': turma.serie
    }
    return base_get_desempenho(*columns, **filters).order_by('exercicio__aula')


def get_desempenho_alunos_reforco_filtrado_por_turma(turma, prova_brasil):
    columns = {'id', 'nome', 'acertos', 'ttl_exercicios', 'indice'}
    filters = {
        'turma': turma
    }

    return base_get_desempenho_alunos(*columns, **filters).order_by('indice')


def get_desempenho_disciplinas_filtrado_por_aluno(escola, aluno, prova_brasil):
    columns = {
        'disciplina',
        'disciplina__nome'
    }
    filters = {
        'aluno': aluno,
        'escola': escola,
        'serie': aluno.serie_atual,
        'is_prova_brasil': prova_brasil
    }
    return base_get_desempenho(*columns, **filters).order_by('indice')


def get_desempenho_descritores(escola, serie, disciplina):
    columns = {
        'exercicio__descritor',
        'exercicio__descritor__cod',
        'exercicio__descritor__descricao'
    }
    filters = {
        'escola': escola,
        'disciplina': disciplina,
        'serie': serie
    }
    return base_get_desempenho(*columns, **filters).order_by('indice')


def get_desempenho_descritores_aluno(escola, aluno, disciplina):
    columns = {
        'exercicio__descritor',
        'exercicio__descritor__cod',
        'exercicio__descritor__descricao'
    }
    filters = {
        'escola': escola,
        'disciplina': disciplina,
        'serie': aluno.serie_atual,
        'aluno': aluno
    }
    return base_get_desempenho(*columns, **filters).order_by('indice')


def get_desempenho_assuntos_filtrado_por_disciplina_e_aluno(escola, disciplina, aluno):
    columns = {
        'exercicio__aula',
        'exercicio__aula__assunto',
        'exercicio__aula__ordem'
    }
    filters = {
        'escola': escola,
        'disciplina': disciplina,
        'aluno': aluno,
        'serie': aluno.serie_atual
    }
    return base_get_desempenho(*columns, **filters).order_by('indice')