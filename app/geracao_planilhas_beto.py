from django.db.models import Q, F
from django.http import HttpResponse

from app.models import Escola, Disciplina, Aluno, HistoricoAulasAssistidas, Descritor, SuperEnsinoUser, Professor, \
    UserSchoolRelationshipManager
from data.wharehouse.models import ExercisesDataWharehouse


class CalculoAux():
    def criar_arquivo(self, nome, queryset, header, row_format):
        arq = open(nome, 'w+')
        arq.write(header)

        for dado in queryset:
            try:
                arq.write(row_format % dado)
            except:
                arq.close()

        arq.close()

    def porcentagem_virgula(self, porc):
        string = str(porc)
        string = string.replace('.', ',')
        return string

    def calcula_questoes_corretas_porc(self, corretas, totais):
        try:
            porcentagem_corretas = round(
                (corretas * 100 / totais),
                2)
            porcentagem_corretas = self.porcentagem_virgula(porcentagem_corretas)

        except ZeroDivisionError:
            porcentagem_corretas = 0

        return porcentagem_corretas

class PlanilhaDadosSerie(CalculoAux):
    def infos(self, *series):
        escolas = Escola.objects.all().order_by('nome')
        portugues = Disciplina.objects.get(nome__icontains='portu', is_prova_brasil=True)
        matematica = Disciplina.objects.get(nome__icontains='matemática', is_prova_brasil=True)
        disciplinas = [portugues, matematica]

        try:
            arq = open('estatisticas_escolas%s.csv' % series, 'w+')
        except TypeError:
            arq = open('estatisticas_escolas.csv', 'w+')

        arq.write(
            'Escola;Alunos em que foram implantados;Alunos que responderam exercício;Engajamento;Vídeos assistidos;Questões respondidas;Questões corretas (Português - %);Questões corretas (Matemática - %);Distrito\n')

        for e in escolas:

            if e.turma_set.filter(serie__in=series).count() == 0:
                continue

            nome_escola = e.nome

            # Engajamento da escola
            quantidade_alunos_escola = Aluno.objects.filter(escola=e, serie_atual__in=series).count()
            quantidade_alunos_responderam_exercicio = ExercisesDataWharehouse.objects.filter(escola=e,
                                                                                             disciplina__in=disciplinas) \
                .series(series).distinct('aluno').count()
            engajamento = round((quantidade_alunos_responderam_exercicio * 100 / quantidade_alunos_escola), 2)
            engajamento = self.porcentagem_virgula(engajamento)

            # Quantidade de vídeos assistidos
            videos_assistidos = HistoricoAulasAssistidas.objects.is_prova_brasil(True).escola(e) \
                .filter(Q(aluno__serie_atual=5) | Q(aluno__serie_atual=9)).count()

            # Questões respondidas
            questoes_respondidas_escola = ExercisesDataWharehouse.objects.get_exercicios_respondidos_escola(e) \
                .is_prova_brasil(True).series(series)
            quantidade_questoes_respondidas_escola = questoes_respondidas_escola.count()

            # Porcentagem de questões respondidas - Português
            #quantidade_questoes_portugues = Exercicio.objects.filter(aula__disciplina=portugues).count()
            questoes_portugues = questoes_respondidas_escola.disciplinas([portugues])
            quantidade_questoes_portugues = questoes_portugues.count()
            quantidade_questoes_certas_portugues = questoes_portugues\
                .filter(gabarito__correta=F('resposta__correta')).count()

            try:
                porcentagem_portugues = round((quantidade_questoes_certas_portugues * 100 / quantidade_questoes_portugues),
                                              2)
                porcentagem_portugues = self.porcentagem_virgula(porcentagem_portugues)

            except ZeroDivisionError:
                porcentagem_portugues = 0

            # Porcentagem de questões respondidas - Matemática
            #quantidade_questoes_matematica = Exercicio.objects.filter(aula__disciplina=matematica).count()
            questoes_matematica = questoes_respondidas_escola.disciplinas([matematica])
            quantidade_questoes_matematica = questoes_matematica.count()
            quantidade_questoes_certas_matematica = questoes_matematica\
                .filter(gabarito__correta=F('resposta__correta')).count()

            try:
                porcentagem_matematica = round(
                    (quantidade_questoes_certas_matematica * 100 / quantidade_questoes_matematica), 2)
                porcentagem_matematica = self.porcentagem_virgula(porcentagem_matematica)

            except ZeroDivisionError:
                porcentagem_matematica = 0

            # Distrito da escola
            distrito = e.distrito.nome

            # 'Escola, Alunos em que foram implantados, Alunos que responderam exercício,' \
            # 'Engajamento, Vídeos assistidos, Questões respondidas,Questões corretas (Português - %),' \
            # 'Questões corretas (Matemática - %),Distrito\n')


            arq.write('%s;%s;%s;%s%%;%s;%s;%s%%;%s%%;%s\n' % (
            nome_escola, quantidade_alunos_escola, quantidade_alunos_responderam_exercicio,
            engajamento, videos_assistidos, quantidade_questoes_respondidas_escola, porcentagem_portugues,
            porcentagem_matematica, distrito))

        arq.close()

    def info_5_ano(self):
        self.infos(5)

    def info_9_ano(self):
        self.infos(9)

    def gerar_planilha(self):
        self.info_5_ano()
        self.info_9_ano()
        self.infos(5,9)


class PlanilhaDescritores(CalculoAux):
    def dados_descritores(self, descritores):
        dados = []

        for descritor in descritores:
            # Questões respondidas
            questoes_respondidas_descritor = ExercisesDataWharehouse.objects.filter(exercicio__descritor=descritor)
            quantidade_questoes_respondidas_descritor = questoes_respondidas_descritor.count()

            # Porcentagem de acertos - Português
            quantidade_questoes_corretas = questoes_respondidas_descritor \
                .filter(gabarito__correta=F('resposta__correta')).count()

            porc_corretas_descritor = self.calcula_questoes_corretas_porc(quantidade_questoes_corretas,
                                                                          quantidade_questoes_respondidas_descritor)

            dados.append((descritor.cod, descritor.disciplina.nome, quantidade_questoes_respondidas_descritor,
                          porc_corretas_descritor))

        return dados

    def gerar_planilha_descritores(self):
        portugues = Disciplina.objects.get(nome__icontains='portu', is_prova_brasil=True)
        descritores_port = Descritor.objects.filter(disciplina=portugues)

        descritores_port_5 = descritores_port.filter(serie=5)
        descritores_port_9 = descritores_port.filter(serie=9)

        matematica = Disciplina.objects.get(nome__icontains='matemática', is_prova_brasil=True)
        descritores_mat = Descritor.objects.filter(disciplina=matematica)

        descritores_mat_5 = descritores_mat.filter(serie=5)
        descritores_mat_9 = descritores_mat.filter(serie=9)

        descritores_5 = descritores_port_5 | descritores_mat_5
        descritores_9 = descritores_port_9 | descritores_mat_9

        dados_5 = self.dados_descritores(descritores_5.order_by('disciplina'))
        dados_9 = self.dados_descritores(descritores_9.order_by('disciplina'))

        header = 'Descritor;Disciplina;Questões respondidas;Porcentagem de acertos\n'
        row_format = '%s;%s;%s;%s%%\n'

        self.criar_arquivo('estatisticas_desc_5.csv', dados_5, header, row_format)
        self.criar_arquivo('estatisticas_desc_9.csv', dados_9, header, row_format)


class PlanilhaEscolaDescritores(CalculoAux):
    def dados_descritores(self, descritores):

        escolas = Escola.objects.order_by('nome')

        dados = []

        for e in escolas:

            if not e.distrito or e.aluno_set.count() == 0:
                continue

            for descritor in descritores:
                # Questões respondidas
                questoes_respondidas_descritor = ExercisesDataWharehouse.objects\
                    .filter(exercicio__descritor=descritor, escola=e)
                quantidade_questoes_respondidas_descritor = questoes_respondidas_descritor.count()

                # Porcentagem de acertos - Português
                quantidade_questoes_corretas = questoes_respondidas_descritor \
                    .filter(gabarito__correta=F('resposta__correta')).count()

                porc_corretas_descritor = self.calcula_questoes_corretas_porc(quantidade_questoes_corretas,
                                                                              quantidade_questoes_respondidas_descritor)

                dados.append((e.nome, descritor.cod, descritor.disciplina.nome, descritor.serie,
                              quantidade_questoes_respondidas_descritor, porc_corretas_descritor, e.distrito.nome))

        return dados

    def gerar_planilha(self):
        portugues = Disciplina.objects.get(nome__icontains='portu', is_prova_brasil=True)
        descritores_port = Descritor.objects.filter(disciplina=portugues).order_by('serie', 'disciplina')

        matematica = Disciplina.objects.get(nome__icontains='matemática', is_prova_brasil=True)
        descritores_mat = Descritor.objects.filter(disciplina=matematica).order_by('serie', 'disciplina')

        descritores = descritores_port | descritores_mat

        dados = self.dados_descritores(descritores)

        header = 'Escola;Descritor;Disciplina;Ano;Questões respondidas;Questões corretas (%%);Distrito\n'
        row_format = '%s;%s;%s;%s;%s;%s%%;%s\n'

        self.criar_arquivo('estatisticas_desc_escolas', dados, header, row_format)

def papaya(request):
    data = []

    seu_list = SuperEnsinoUser.objects.all()
    prof_list = Professor.objects.all()

    queryset_list = list(seu_list)[:-2] + list(prof_list)

    for gest_prof in queryset_list:
        nome = gest_prof.nome
        username = gest_prof.user.username
        relations = UserSchoolRelationshipManager.objects.filter(user=gest_prof.user)

        distrito = 'NÃO POSSUI'

        if gest_prof.role == 8:
            distrito = 'TODOS' if relations.count() >= 50 else relations[0].escola.distrito

        if gest_prof.role == 4:
            distrito = distrito if gest_prof.escola.count() == 0 else gest_prof.escola.all()[0].distrito.nome

        escola = 'NÃO POSSUI'

        if gest_prof.role != 8:
            escolas_count = gest_prof.escola.all().count()
            escola = gest_prof.escola.all()[0].nome if escolas_count > 0 else escola
        else:
            escola = 'TODAS DO DISTRITO'

        quantidade_acessos = AccessToken.objects.filter(user=gest_prof.user).count()
        cargo = 'PROFESSOR' if gest_prof.role != 8 else 'GESTOR'

        data.append((nome, username, cargo, distrito, escola, quantidade_acessos))

    file = open('estatisticas_gestores_professores.csv', 'w+')

    file.write('Nome,Login,Cargo,Distrito,Escola,Quantidade de acessos\n')

    for datum in data:
        file.write('%s,%s,%s,%s,%s,%s\n' % (datum[0], datum[1], datum[2], datum[3], datum[4], datum[5]))

    file.close()

    return HttpResponse({})