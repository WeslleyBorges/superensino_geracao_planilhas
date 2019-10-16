from app import models as m
from django.db import models


def get_filtered_desempenho_assuntos(
        turma, serie, disciplina, is_prova_brasil=False):
    """Retorna o desempenho de acertos e erros de acordo com os filtros.

    Os filtros são opcionais, no entanto, pelo menos um deles deve ser diferen-
    te de None.
    """
    desempenho = m.Resposta.objects.is_prova_brasil(is_prova_brasil)
    if turma:
        desempenho.turma(turma)
    if serie:
        desempenho.serie(serie)
    if disciplina:
        desempenho.disciplina(disciplina)

    return desempenho.desempenho_aula().order_by(
        'aproveitamento', 'exercicio__aula__assunto')


def get_desempenho_por_serie(escola, is_prova_brasil):
    """
    Retorna o demonstrativo resumido do desempenho das séries da escola. O parâmetro
    is_prova_brasil, determina se os dados devem ser de exercícios de reforço ou
    prova Brasil.
    """
    qs = m.Turma.objects.filter(escola__id=escola)
    # Filtra especificamente as séries que a escola atende com base nas turmas
    # que estão cadastradas.
    serie_ids = set(turma.serie for turma in qs)
    return m.Resposta.objects.filter(
        exercicio__aula__serie__in=serie_ids).turmas(qs).is_prova_brasil(
        is_prova_brasil).desempenho()


def desempenho_super_reforco_por_turma():
    # resultset = m.Resposta.objects.values(
    #    'aluno__turma__serie').annotate(models.Count('exercicio'))
    resultset = m.Resposta.objects.filter(
        exercicio__aula__disciplina__is_prova_brasil=False).values(
     'aluno__turma').annotate(
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
     ).order_by('aluno__turma__serie')

    return resultset


def desempenho_prova_brasil_por_turma():
    """DEPRECATED: Método movido para RespostaQuerySet."""
    resultset = m.Resposta.objects.filter(
        exercicio__aula__disciplina__is_prova_brasil=True).values(
     'aluno__turma').annotate(
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
     ).order_by('aluno__turma__serie')

    return resultset


def consulta_analitica_por_serie_prova_brasil(escola, serie):
    resultset = m.Resposta.objects.filter(
        aluno__turma__escola__id=escola,
        exercicio__aula__disciplina__is_prova_brasil=True,
        exercicio__aula__serie=serie).values(
     'exercicio__aula__disciplina', 'exercicio__aula__disciplina__nome').annotate(
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


def consulta_analitica_por_serie_super_reforco(escola, serie):
    resultset = m.Resposta.objects.filter(
        aluno__turma__escola__id=escola,
        exercicio__aula__disciplina__is_prova_brasil=False,
        exercicio__aula__serie=serie).values(
     'exercicio__aula__disciplina', 'exercicio__aula__disciplina__nome').annotate(
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


def consulta_sintetica_por_serie_prova_brasil(serie):
    # README: Moving this method to RespostaQuerySet
    resultset = m.Resposta.objects.filter(
        exercicio__aula__disciplina__is_prova_brasil=True,
        exercicio__aula__serie=serie).values(
     'exercicio__aula__disciplina', 'exercicio__aula__disciplina__nome').annotate(
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


def consulta_sintetica_por_serie_super_reforco(serie):
    resultset = m.Resposta.objects.filter(
        exercicio__aula__disciplina__is_prova_brasil=False,
        exercicio__aula__serie=serie).values(
     'exercicio__aula__disciplina', 'exercicio__aula__disciplina__nome').annotate(
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


def consulta_descritores_por_disciplina_serie(disciplina, serie, escola):
    resultset = m.Resposta.objects.filter(
        aluno__escola_id=escola,
        exercicio__aula__disciplina_id=disciplina,
        exercicio__aula__serie=serie).values(
     'exercicio__descritor', 'exercicio__descritor__cod', 'exercicio__descritor__descricao').annotate(
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
     ).order_by('exercicio__descritor')

    return resultset


def consulta_analitica_por_turma(turma, is_prova_brasil=False):
    resultset = m.Resposta.objects.filter(
        exercicio__aula__disciplina__is_prova_brasil=is_prova_brasil,
        aluno__turma=turma).values(
     'exercicio__aula__disciplina', 'exercicio__aula__disciplina__nome').annotate(
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
     ).order_by('aproveitamento','exercicio__aula__disciplina')

    return resultset


def consulta_descritores_por_disciplina_turma(disciplina, turma):
    resultset = m.Resposta.objects.filter(
        exercicio__aula__disciplina_id=disciplina,
        aluno__turma=turma).values(
     'exercicio__descritor', 'exercicio__descritor__cod', 'exercicio__descritor__descricao').annotate(
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
     ).order_by('aproveitamento')

    return resultset


def consulta_descritores_por_disciplina_aluno(disciplina, aluno):
    """
    Consulta o desempenho dos descritores de uma disciplina por aluno
    """
    resultset = m.Resposta.objects.filter(
        exercicio__aula__disciplina_id=disciplina,
        aluno=aluno).values(
     'exercicio__descritor', 'exercicio__descritor__cod', 'exercicio__descritor__descricao').annotate(
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
             'corretas')*100(models.F('corretas') + models.F('erradas'))
     ).order_by('aproveitamento')

    return resultset


def consulta_assuntos_por_disciplina_aluno(disciplina, aluno):
    """
    Consulta o desempenho de um assunto de uma disciplina por aluno
    """
    resultset = m.Resposta.objects.filter(
        exercicio__aula__disciplina_id=disciplina,
        aluno=aluno).values(
     'exercicio__aula', 'exercicio__aula__assunto', 'exercicio__aula__ordem').annotate(
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
     ).order_by('aproveitamento', 'exercicio__aula__assunto', 'exercicio__aula__ordem')

    return resultset


def get_alunos_from_responsavel_by_user(user):
    responsavel = m.Responsavel.objects.get(user=user)
    queryset = m.Aluno.objects.filter(
        responsaveis=responsavel).values(
        'id', 'imagem', 'nome', 'turma__serie'
        )
    return queryset


def consulta_aulas_assistidas_dia(aluno, data):
    query = m.HistoricoAulasAssistidas.objects.filter(
        aluno=aluno, timestamp__date=data).order_by('aula__disciplina')
    return query


def get_aulas_por_nome_disciplina(nome):
    return m.Aula.objects.filter(disciplina__nome=nome)


def get_aluno_por_email(email):
    return m.Aluno.objects.get(user__email=email)


def get_total_de_aulas_por_disciplina(aluno, mes, ano):
    queryset = m.HistoricoAulasAssistidas.objects.filter(
        aluno=aluno,
        timestamp__date__month=mes,
        timestamp__date__year=ano).values(
            'aula__disciplina', 'aula__disciplina__nome').annotate(
            models.Count('aula'))

    return queryset


def get_exercicios_por_assunto(assunto):
    return m.Exercicio.objects.filter(aula__assunto=assunto)


def consulta_exercicios_realizados_dia(aluno, data):
    resultset = m.Resposta.objects.filter(
        aluno=aluno,
        date=data).values(
     'exercicio__aula',
     'exercicio__aula__disciplina__nome',
     'exercicio__aula__assunto',
     'date').annotate(
         maxtimestamp=models.Max('timestamp'),
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
     )

    return resultset


def consulta_exercicios_realizados_mes(aluno, mes, ano):
    resultset = m.Resposta.objects.filter(
        aluno=aluno,
        date__month=mes, date__year=ano).values(
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
     )

    return resultset


def consulta_turmas_por_status(status):
    return m.Turma.objects.filter(status=status)


def consulta_escolas_por_usuario(user, distrito=None, bairro=None):

    if distrito is not None and bairro is not None:
        filters = {'distrito_id': distrito, 'endereco__bairro__unaccent__icontains': bairro}

    if distrito is not None and bairro is None:
        filters = {'distrito_id': distrito}

    if bairro is not None and distrito is None:
        filters = {'endereco__bairro__unaccent__icontains': bairro}

    if distrito is None and bairro is None:
        filters = {}

    profile = m.Profile.objects.get(user=user)

    if profile.role == m.Profile.GESTOR_ESCOLAR:
        return m.Escola.objects.filter(gestor__id=profile.id, **filters)
    elif profile.role == m.Profile.SUPER_ENSINO_USER:
        return m.Escola.objects.filter(userschoolrelationshipmanager__user=profile.user, **filters)
    elif profile.role == m.Profile.PROFESSOR:
        professor = m.Professor.objects.get(user=user)
        return professor.escola.filter(**filters)


def consulta_total_alunos_escola(escola):
    resultset = m.Aluno.objects.filter(turma__escola=escola)
    return resultset.count()


def consulta_aulas_assistidas_por_disciplina(
        aluno, serie, disciplina, bimestre=None):
    query = m.HistoricoAulasAssistidas.objects.filter(
        aluno=aluno, aula__serie=serie, aula__disciplina=disciplina)

    if not disciplina.is_prova_brasil:
        query = query.filter(aula__bimestre=bimestre)

    return query.distinct('aula')


# def get_total_de_aulas_por_disciplina(serie, disciplina, bimestre=None):
#     qs = m.Aula.objects.filter(disciplina=disciplina, serie=serie)
#
#     if not disciplina.is_prova_brasil and bimestre is not None:
#         qs = qs.filter(bimestre=bimestre)
#
#     return qs.count()


def consulta_desempenho_aluno(aluno, serie, disciplina, bimestre=None):
    resultset = m.Resposta.objects.filter(
        aluno=aluno,
        exercicio__aula__serie=serie,
        exercicio__aula__disciplina=disciplina).values(
     'exercicio__aula__serie').annotate(
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
     ).order_by('exercicio__aula__serie')

    return resultset


#def consulta_total_aulas_assunto(aula):
