from data.wharehouse.models import ExercisesDataWharehouse
from app.models import (HistoricoAulasAssistidas, Attachment, Exercicio, Aluno,
    Turma, Disciplina)
from django.db import models
from django.db.models import F
from api.reports import commons


def calculate_turma_ranking(escola, disciplina, serie, bim=1):
    """
    Retorna um dictionary em ordem decrescente de índice de desempenho. A posição
    da turma no dict determina o seu ranqueamentoself.
    """
    rs = ExercisesDataWharehouse.objects.filter(
            turma__escola=escola,
            disciplina=disciplina,
            exercicio__aula__bimestre=bim,
            exercicio__aula__serie=serie).values(
            'turma',
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
        indice=F('correta') * 100 / F('exercicios_realizados')
    ).order_by('-indice')

    return rs


def get_turma_rank_position(turma, disciplina, serie, bim=1):
    """Retorna a posição numérica que a turma se encontra frente as outras de mesma,
    disciplina, serie, escola e bimestre."""

    rs = calculate_turma_ranking(turma.escola, disciplina, serie, bim)
    total = len(rs)
    pos = 1
    indice_anterior = -1

    for r in rs:
        indice_atual = r['indice']
        if r['turma'] == turma.id:
            break
        else:
            if indice_anterior != -1:
                if indice_atual < indice_anterior:
                    pos += 1
            indice_anterior = indice_atual

    return {'total': total, 'pos': pos}


def calculate_indice_turma_acumulado(turma, disciplina, bim_ref=1):
    """
    Calcula a média acumulada do índice de desempenho da turma no ano corrente.
    """
    rs = ExercisesDataWharehouse.objects.filter(
        disciplina=disciplina, turma=turma, exercicio__aula__bimestre__lte=bim_ref).values(
        'turma__identificador',
        'exercicio__aula__bimestre',
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
    ).aggregate(models.Sum('indice'))
    acumulado = rs['indice__sum']/bim_ref
    return acumulado


def _get_total_video_aulas_disciplina(disciplina, serie, bimestre):
    return Attachment.objects.filter(
        aula__disciplina=disciplina,
        aula__bimestre=bimestre,
        aula__serie=serie).count()


def calculate_turma_details(turma, disciplina, bim=1):
    """Calcula os detalhes de desempenho da turma.

    Dada turma e disciplina o método calcula as seguintes estatísticas para
    a turma:
        * número de alunos da turma
        * índice da turma calculado com base nos erros e acertos dos alunos
        * total de exercício realizados pelos alunos
        * total de erros
        * total de acertos
        * percentual de vídeos assistidos pela turma dentro do bimestre
        * Acumulado com o somatório dos índices de todos os bimestres.
        * Nota máxima e mínima obtida nos exercícios dentro do bimestre
        * Posição da turma em relação as demais

    O resultado é retornado em um dictionary. Caso a turma não tenha dados
    suficientes para geração de estatísticas um o dictionary vazio é retornado.
    """
    # Obtém: índice turma, ex. realizados, erros, acertos, max e mín.
    rs = ExercisesDataWharehouse.objects.\
        get_desempenho_turma_disciplina_details(turma, disciplina, bim)

    if rs is None:
        return {}

    nr_alunos = turma.alunos.count()

    total_de_aulas_disc_bim = Attachment.objects.filter(
        aula__disciplina=disciplina, aula__bimestre=bim, aula__serie=turma.serie).count()

    if total_de_aulas_disc_bim > 0:
        qsuniqueviews = HistoricoAulasAssistidas.objects.filter(
            aluno__in=turma.alunos.all(),
            aula__serie=turma.serie,
            aula__bimestre=bim,
            aula__disciplina__id=disciplina.id).values('aula__disciplina').annotate(
            unique_views=models.Count('attachment__id', distinct=True))

        if qsuniqueviews.count() > 0:
            uniqueviews_count = qsuniqueviews[0]['unique_views']
        else:
            uniqueviews_count = 0

        percentual_videos = uniqueviews_count * 100 / total_de_aulas_disc_bim
    else:
        percentual_videos = 0

    acumulado = calculate_indice_turma_acumulado(turma, disciplina, 2)
    rank_dict = get_turma_rank_position(turma, disciplina, turma.serie)

    data = {
        'turma': "{0} - {1}".format(turma.display_name(), disciplina.nome),

        # Dados da escola para navegação
        'escola': {
            'id': turma.escola.id,
            'nome': turma.escola.nome,
            'distrito': turma.escola.distrito.nome
        },
        # Número de alunos inscritos na turma
        'qdeAlunos': nr_alunos,
        # O índice da turma é obtido através da relação de exercícios resolvi-
        # dos corretamente dividido pelo total de exercícios resolvidos.
        'indTurma': rs['indice_turma'],
        # Contagem do total de exercícios realizados incluído aqueles que foram
        # respondidos corretamente e os que o aluno errou.
        'exRealizados': rs['exercicios_realizados'],
        'exTotal': commons.get_total_exercicios_disciplina(disciplina.id, bim, turma.serie) * nr_alunos,
        # Contagem do total de questões corretas
        'acertos': rs['acertos'],
        # Contagem do total de questões incorretas
        'erros': rs['erros'],
        # Índice de aluno mais alto obtido nos assuntos da disciplina
        'indMax': rs['max'],
        # Índice de aluno mais baixo obtido nos assuntos da disciplina
        'indMin': rs['min'],
        # Percentual de visualizações da turma. Esse número é obtido através do
        # somatório do percentual de vídeos assistidos dos alunos pela quanti-
        # dade dos alunos que assitiram os vídeos.
        'perVideosAssistidos': int(percentual_videos),
        'indGeral': acumulado,
        'totalRanque': rank_dict['total'],
        'posicaoRanque': rank_dict['pos'],
        'idBimestre': bim
    }

    return data


def get_melhor_desempenho_disciplina_turma(disciplina, turma):
    """
    Retorna no melhor desempenho da turma.

    TODO: Unificar esse método com o get_pior_desempenho_disciplina_turma
    """
    return ExercisesDataWharehouse.objects.filter(
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


def get_pior_desempenho_disciplina_turma(disciplina, turma):
    """
    Retorna o pior desempenho da turma.

    TODO: Unificar esse método com o get_melhor_desempenho_disciplina_turma
    """
    return ExercisesDataWharehouse.objects.filter(
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


def get_max_aluno(aluno, turma, disciplina, bimestre):
    """Calcula a melhor nota do aluno com base nos assuntos."""
    queryset = ExercisesDataWharehouse.objects.\
        get_desempenho_individual_disciplina(
            aluno, turma, disciplina, bimestre)
    return queryset.aggregate(m=models.Max(F('indice')))['m']


def get_min_aluno(aluno, turma, disciplina, bimestre):
    """Calcula a melhor nota do aluno com base nos assuntos."""
    queryset = ExercisesDataWharehouse.objects.\
        get_desempenho_individual_disciplina(
            aluno, turma, disciplina, bimestre)
    return queryset.aggregate(m=models.Min(F('indice')))['m']


def consulta_turmas_professor(professor, escola, bimestre=1):
    """Retorna o quadro geral de turmas-disciplinas do professor."""
    disciplinas = professor.get_disciplinas_ids(escola)
    turmas = Turma.objects.filter(turmas=professor, escola=escola).distinct()

    rs = ExercisesDataWharehouse.objects.filter(
        escola=escola,
        turma__in=turmas,
        disciplina__id__in=disciplinas).values(
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
                indice=F('correta') * 100 / F('exercicios_realizados')
            ).order_by('turma__identificador')

    data = []

    for d in rs:
        exercicios_total = Exercicio.objects.filter(
            aula__disciplina__id=d['disciplina'],
            aula__serie=d['turma__serie'],
            aula__bimestre=bimestre).count()

        turma = Turma.objects.get(pk=d['turma'])
        disciplina = Disciplina.objects.get(pk=d['disciplina'])
        rank_dict = get_turma_rank_position(turma, disciplina, turma.serie)

        total_alunos = turma.objects.count()
        total_exercicios_resolvidos = d['exercicios_realizados']

        # Obtém o percentual do nr. de exercícios resolvidos pelo máximo possível de exercícios a realizar que é
        # obtido, pela multiplicação do total de exercícios da disciplina pelo total de alunos da turma.
        percent_exercicios_realizados_turma = (total_exercicios_resolvidos * 100) / (exercicios_total * total_alunos)

        turma_obj = {
            'turma': d['turma__identificador'],
            'turmaId': d['turma'],
            'indice': int(d['indice']),
            'disciplina': d['disciplina__nome'],
            'disciplinaId': d['disciplina'],
            'escola': d['escola__nome'],
            'totalAcertos': d['correta'],
            'totalErros': d['exercicios_realizados'] - d['correta'],
            'maxNota': get_melhor_desempenho_disciplina_turma(disciplina, turma),
            'minNota': get_pior_desempenho_disciplina_turma(disciplina, turma),
            'exerciciosResolvidos': total_exercicios_resolvidos,
            'totalExercicios': exercicios_total,
            'classificacaoDisciplina': rank_dict['pos'],
            'totalDisciplina': rank_dict['total'],
            'percentExerciciosRealizados': percent_exercicios_realizados_turma
        }

        data.append(turma_obj)

    return data


def query_consulta_desempenho_alunos_turma(turma, disciplina, bim):
    """Retorna um result set contendo o desempenho dos alunos."""
    queryset = ExercisesDataWharehouse.objects.filter(
        disciplina=disciplina,
        turma=turma,
        exercicio__aula__bimestre=bim).values(
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
        indice=F('acertos') * 100 / F('ttl_exercicios')
    )

    return queryset


def get_desempenho_de_alunos(turma, disciplina, bim, indice_turma):
    """Retorna o desempenho de alunos por turma, disciplina e bimestre."""
    desempenho_alunos = ExercisesDataWharehouse.objects.\
        get_desempenho_de_alunos_por_disciplina(disciplina, turma, bim)

    ttl_video_aulas = _get_total_video_aulas_disciplina(
        disciplina, turma.serie, bim)

    ttl_exercicios_bim = Exercicio.objects.bimestre_filtered(
        disciplina, turma.serie, bim).count()

    data = []

    for item in desempenho_alunos:
        aluno = Aluno.objects.get(pk=item['aluno'])
        views = HistoricoAulasAssistidas.objects.aluno_views(
            aluno, disciplina, turma.serie, bim).count()

        obj = {
            'aluno': item['aluno__nome'],
            'alunoId': item['aluno'],
            'indTurma': indice_turma,
            'exRealizados': item['ttl_exercicios'],
            'exTotal': ttl_exercicios_bim,
            'erros': item['erros'],
            'acertos': item['acertos'],
            'videosAssistidos': views,
            'videosTotal': ttl_video_aulas,
            'indGeral': item['indice'],
            'indMin': get_min_aluno(aluno, turma, disciplina, bim),
            'indMax': get_max_aluno(aluno, turma, disciplina, bim),
            'posicaoRanque': 0,
            'totalRanque': 0,
            'classes': "active contracted",
        }

        data.append(obj)

    return data


def get_desempenho_assuntos(turma, disciplina, bimestre, indice_turma):
    """Retorna o desempenho por assuntos da disciplina."""
    desempenho_assuntos = ExercisesDataWharehouse.objects.\
        desempenho_turma_assuntos(disciplina, turma, bimestre)

    ttl_exercicios_bim = Exercicio.objects.bimestre_filtered(
        disciplina, turma.serie, bimestre).count()

    ttl_video_aulas = _get_total_video_aulas_disciplina(
        disciplina, turma.serie, bimestre)

    data = []
    for item in desempenho_assuntos:
        obj = {
            'assunto': item['exercicio__aula__assunto'],
            'assuntoId': item['exercicio__aula'],
            'indTurma': indice_turma,
            'exRealizados': item['ttl_exercicios'],
            'exTotal': ttl_exercicios_bim,
            'erros': item['erros'],
            'acertos': item['acertos'],
            'videosAssistidos': 87,
            'videosTotal': ttl_video_aulas,
            'indGeral': item['indice'],
            'indMin': 68,
            'indMax': 123,
            'posicaoRanque': 0,
            'totalRanque': 0,
            'classes': "active contracted",
        }

        data.append(obj)

    return data


def get_desempenho_disciplinas(escola, serie, provabrasil):
    queryset = ExercisesDataWharehouse.objects.filter(
        aluno__escola=escola,
        exercicio__aula__disciplina__is_prova_brasil=provabrasil,
        exercicio__aula__serie=serie).values(
        'disciplina',
        'disciplina__nome'
    ).annotate(
        acertos=models.Sum(
            models.Case(
                models.When(resposta=F('gabarito'), then=1), default=0,
                output_field=models.IntegerField()
            )
        ),
        ttl_exercicios=models.Count('exercicio'),
        indice=F('acertos') * 100 / F('ttl_exercicios')
    )

    return queryset
