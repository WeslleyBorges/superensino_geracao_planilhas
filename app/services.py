from app.models import HistoricoAulasAssistidas, Aula
from app.models import Aluno, Resposta, Exercicio, Attachment, Turma


def get_historico_aulas_assitidas_serie(escola, serie, is_prova_brasil=False):
    return HistoricoAulasAssistidas.objects.is_prova_brasil(
        is_prova_brasil).escola(escola).serie(serie)


def get_serie_summary(escola, serie, is_prova_brasil=False):
    """Recupera os dados do cabeçalho do relatório de desempenho de serie
    do Super Gestor. O resultado final é um dictionary para ser serializado
    pela API do DRF"""
    data = {
        'aulas_assistidas':
            HistoricoAulasAssistidas.objects.is_prova_brasil(
                is_prova_brasil).escola(escola).serie(serie).count(),
        'visualizacoes_unicas':
            HistoricoAulasAssistidas.objects.is_prova_brasil(
                is_prova_brasil).escola(escola).serie(serie).distinct('aluno').count(),
        'total_alunos': Aluno.objects.count_alunos_by_serie(escola, serie)
    }

    return data


def get_all_turmas(escola, serie):
    queryset = Turma.objects.filter(serie=serie, escola=escola)
    return queryset


def get_desempenho_individual_por_disciplina(
        aluno, disciplina, serie, bimestre, is_prova_brasil=False):
    """Retorna o desempenho individual do aluno.

    O retorno é composto por id da disciplina, nome da disciplina, o total de
    aulas da disciplina, o total de aulas visualizadas pelo aluno, o total de
    exercícios da disciplina, o total de exercícios realizados, total de
    acertos.
    Dentro da mesma pesquisa é retornado ainda, por assunto:
        - id do assunto;
        - nome do assunto;
        - total de aulas do assuntos;
        - total de aulas do assunto assistidas;
        - total de Exercícios;
        - total de exercícios realizados;
        - numero de acertos;
    """
    hist_aulas = Aula.objects.filter(
        historicoaulasassistidas__aluno=aluno,
        historicoaulasassistidas__aula__disciplina__is_prova_brasil=is_prova_brasil,
        historicoaulasassistidas__aula__serie=serie,
        historicoaulasassistidas__aula__disciplina=disciplina)

    filter_assunto = Resposta.objects.filter(
        aluno=aluno,
        exercicio__aula__serie=serie,
        exercicio__aula__disciplina=disciplina)

    total_exercicios_filter = Exercicio.objects.filter(
        aula__disciplina=disciplina,
        aula__serie=serie)

    if bimestre is not None:
        hist_aulas.filter(historicoaulasassistidas__aula__bimestre=bimestre)
        filter_assunto.filter(exercicio__aula__bimestre=bimestre)
        total_exercicios_filter.filter(aula__bimestre=bimestre)

    aulas_resp = Aula.objects.filter(
        assunto__in=filter_assunto.values(
            'exercicio__aula__assunto').distinct('exercicio__aula__assunto'))

    # Obtém a lista de aulas que foram assitidas ou que possuem exercícios
    # respondidos pelo aluno
    aulas = (hist_aulas | aulas_resp).distinct()
    corretas = 0
    total_exercicios = total_exercicios_filter.count()
    total_ex_realizados = 0
    total_aulas_assitidas = 0
    total_aulas = Attachment.objects.aulas_count(serie, disciplina, bimestre)

    assuntos = []
    for a in aulas:
        # Obtém a resposta por aula
        # NOTA: O Resultado esperado é que a resposta seja um array com apenas
        # 1 item.
        if bimestre is not None:
            da = Resposta.objects.select_aluno(
                aluno.id).is_prova_brasil(is_prova_brasil).serie(serie).disciplina(
                disciplina.id).bimestre(bimestre).aula(a).desempenho_aula()

            qt_exercicios = Exercicio.objects.filter(aula=a.id, aula__bimestre=bimestre, aula__serie=serie).count()
            qt_aulas = Attachment.objects.aulas_por_assunto(a.id, bimestre).count()
            aulas_assist = HistoricoAulasAssistidas.objects.get_aluno(
                aluno.id).is_prova_brasil(is_prova_brasil).serie(
                serie).bimestre(bimestre).disciplina(disciplina.id).assunto(
                a.id).distinct('aula', 'attachment').count()
        else:
            da = Resposta.objects.select_aluno(
                aluno.id).is_prova_brasil(is_prova_brasil).serie(serie).disciplina(
                disciplina.id).aula(a).desempenho_aula()

            qt_exercicios = Exercicio.objects.filter(aula=a.id, aula__serie=serie).count()
            qt_aulas = Attachment.objects.aulas_por_assunto(a.id, bimestre).count()
            aulas_assist = HistoricoAulasAssistidas.objects.get_aluno(
                aluno.id).is_prova_brasil(is_prova_brasil).serie(
                serie).disciplina(disciplina.id).assunto(
                a.id).distinct('aula', 'attachment').count()

        acertos = 0
        total = 0

        if len(da) > 0:
            acertos += da[0]['corretas']
            total += da[0]['total']

        assuntos.append({
            'assunto_id': a.id,
            'assunto_nome': a.assunto,
            'total_aulas': qt_aulas,
            'aulas_assistidas': aulas_assist,
            'total_exercicios': qt_exercicios,
            'exercicios_realizados': total,
            'num_acertos': acertos
        })

        if len(da) > 0:
            corretas += acertos
            total_ex_realizados += total
        # total_exercicios += qt_exercicios
        total_aulas_assitidas += aulas_assist

    return {
        'disciplina_id': disciplina.id,
        'disciplina_nome': disciplina.nome,
        'total_aulas': total_aulas,
        'aulas_assistidas': total_aulas_assitidas,
        'total_exercicios': total_exercicios,
        'exercicios_realizados': total_ex_realizados,
        'num_acertos': corretas, 'assuntos': assuntos}
