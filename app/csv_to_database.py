from .models import *
from django.contrib.auth import get_user_model
from app.models import Aluno
import re
import logging
from random import randint
from django.template.defaultfilters import slugify

logger = logging.getLogger(__name__)

# Constantes
# Colunas do CSV:
CODIGO_ALUNO = 0
COD_INEP_ALUNO = 1
CPF_RESPONSAVEL = 2
DATA_NASCIMENTO = 3
DISTRITO = 4
EMAIL = 5
INTERVALO_SERIE = 6  # intervalo no qual se encontra a série. Ex: FUND 1º AO 5º ANO
REFERENCIA_ESCOLA = 7
NOME_ESCOLA = 8
COD_INEP_ESCOLA = 9
SERIE_ATUAL = 10
NOME_MAE = 11
NOME_ALUNO = 12
NOME_SOCIAL = 13
NOME_PAI = 14
TELEFONE = 15
LETRA_TURMA = 16
TURNO = 17

# Senha padrão para o usuário
DEFAULT_PASSWORD = '123mudar'

# Quantidade de colunas da planilha
QUANTIDADE_COLUNAS_PLANILHA = 18


def sort_matrix(matrix):
    sorter = lambda x: (x[DISTRITO], x[NOME_ESCOLA],
                        x[INTERVALO_SERIE], x[SERIE_ATUAL],
                        x[LETRA_TURMA], x[TURNO])

    matrix.sort(key=sorter)


def convert_to_matrix(string_arquivo):
    """
    Função responsável por converter para matriz toda a string lida do arquivo csv
    :param string_arquivo:
    :return: <list <list>>
    """

    matrix = []

    # Separa a string em uma lista que representa as linhas do CSV
    matrix_aux = string_arquivo.split('\n')

    for row in matrix_aux:
        # Linha já com as colunas separadas
        separated_row = row.split(',')

        # Se a linha não tiver o número exato de colunas (9),
        # esta linha não será inclusa na matriz.
        # Isto é uma medida de segurança para caso haja linhas vazias
        # no fim do arquivo.

        if len(separated_row) == QUANTIDADE_COLUNAS_PLANILHA:
            matrix.append(separated_row)

    # Retorna a matriz a partir da segunda linha, pois na primeira
    # encontram-se os headers das colunas
    return matrix[1:]


def ler_csv(arquivo):
    """
    Lê o arquivo .csv e retorna os seus dados
    :param arquivo:
    :return:
    """
    dados_csv = []

    dados_csv = convert_to_matrix(arquivo)

    return dados_csv


def distrito_model_object(row):
    """
    Obtém o nome do distrito na linha da iteração atual e o cria, caso não exista, ou recupera-o, caso contrário
    """
    nome_distrito = row[DISTRITO]

    distrito = Distrito.objects.get_or_create(nome=nome_distrito)

    return distrito


def escola_model_object(row):
    """
    Obtém os dados da escola na linha da iteração atual e a cria, caso não exista, ou a recupera, caso contrário
    """
    nome_escola = row[NOME_ESCOLA]
    referencia_escola = int(row[REFERENCIA_ESCOLA])
    codigo_inep = row[COD_INEP_ESCOLA]

    distrito = distrito_model_object(row)[0]

    slug = slugify(nome_escola)

    escola = Escola.objects.get_or_create(
        nome=nome_escola,
        referencia_escola=referencia_escola,
        distrito=distrito,
        codigo_inep=codigo_inep,
        slug=slug
    )

    return escola


def cria_turma_escola_distrito(row):
    """
    Cria a turma com a escola já setada e seu respectivo distrito setado também
    Além disso, retorna uma tupla com a escola e a serie atual da turma
    """
    logger.info('--> cria_turma_escola_distrito')

    turno = row[TURNO]
    letra = row[LETRA_TURMA]
    descricao = row[INTERVALO_SERIE]
    serie = row[SERIE_ATUAL][0]
    identificador = '%s %s' % (serie, letra)

    escola = escola_model_object(row)[0]

    turma = Turma.objects.get_or_create(
        identificador=identificador,
        turno=turno,
        letra=letra,
        descricao=descricao,
        serie=serie,
        escola=escola
    )

    logger.info('<-- cria_turma_escola_distrito')

    return turma[0]


def exists_user_username(username):
    """
    Verifica se existe um usuário com determinado username já criado na base
    """
    return get_user_model().objects.filter(username=username).exists()


def returns_user_number(username):
    """
    Retorna o número que encontra-se no final do username
    """
    number = ''

    for char in username:
        if char.isdigit():
            number += char

    if number:
        return int(number)

    return 0


def lista_prefixo(users_array, username):
    """
    :param users_array:
    :param username:
    :return:
    """
    lista_username = []

    for user in users_array: # tuple_array (username, number)
        if re.search('^' + username + '$', user[0]) or re.search('^' + username + '\d*$', user[0]):
            lista_username.append(user[0])

    return lista_username


def sort_username_tuples(usernames):
    tuple_list = []

    for user in usernames:
        tuple_list.append((user.username, returns_user_number(user.username)))

    tuple_list.sort(key=lambda tup: tup[1])

    return tuple_list


def returns_next_user_name(username):
    """
    Retorna o nome do próximo usuário caso o início dele seja repetido
    """

    # Filtra pelo username com nome iniciado pelo username repetido
    # Ordena em ordem descrescente
    # E retorna a primeira posição, que é onde se encontra o usuário com o maior (ordem alfabética) username repetido
    lista_username_prefixo = get_user_model().objects.filter(username__startswith=username)

    tuplas_usernames = sort_username_tuples(lista_username_prefixo)

    ultimo_username = lista_prefixo(tuplas_usernames, username)[-1]

    # Retorna o número do fim deste username
    username_number = returns_user_number(ultimo_username)

    # Retorna o username concatenado com o número do fim do maior username incrementado
    return username + str(username_number + 1)


def primeiro_sobrenome_significativo(sobrenomes):
    """
    Retorna o primeiro sobrenome significativo da pessoa,
    excluindo-se aqueles nomes mais comuns que são preposição
    ou preposição + artigo
    :param sobrenomes:
    :return:
    """
    sobrenomes_nao_significativos = ['de', 'do', 'dos', 'da', 'das']

    sobrenome_significativo = ''

    for sobrenome in sobrenomes:
        if not sobrenome.lower() in sobrenomes_nao_significativos:
            sobrenome_significativo = sobrenome
            return sobrenome_significativo


def gera_username(nome):
    """
    Gera o username do usuário com base em seu nome
    :param nome:
    :return:
    """
    # Regra da criação do username
    # Primeira letra do primeiro nome concatenada com o sobrenome

    sobrenome = primeiro_sobrenome_significativo(nome.split(' ')[1:])
    username = str(nome.split(' ')[0][0] + sobrenome).lower()

    # Se já existir o usuário cadastrado, faz os devidos tratamentos para evitar a sua repetição
    if exists_user_username(username):
        username = returns_next_user_name(username)

    return username


def cria_aluno(row):
    """
    Retorna o model de aluno com o usuário já criado e setado em aluno
    """
    nome_aluno = row[NOME_ALUNO]
    #nome_social = row[NOME_SOCIAL]
    matricula = row[CODIGO_ALUNO]
    codigo_inep = row[COD_INEP_ALUNO]

    data_nascimento = row[DATA_NASCIMENTO]

    ano = data_nascimento[-4:]
    mes = data_nascimento[-6:-4]
    dia = '0' + data_nascimento[0] if len(data_nascimento) == 7 else data_nascimento[:2]

    data_formatada = '%s-%s-%s' % (ano, mes, dia)

    aluno = Aluno(
        nome=nome_aluno,
        #nome_social=nome_social,
        matricula=matricula,
        data_nascimento=data_formatada,
        codigo_inep=codigo_inep
    )

    return aluno


def cria_responsaveis(row):
    """
    Retorna um dictionary com informações dos responsáveis pelo aluno.
    :param row:
    :return:
    """

    responsaveis = []

    nome_mae = row[NOME_MAE]
    cpf_responsavel = row[CPF_RESPONSAVEL]
    telefone = row[TELEFONE]
    email = row[EMAIL]
    nome_pai = row[NOME_PAI]

    mae = Responsavel(
        nome=nome_mae,
        cpf=cpf_responsavel,
        telefone=telefone,
        email=email
    )

    responsaveis.append(mae)

    if nome_pai != '':
        pai = Responsavel(
            nome=nome_pai
        )
        responsaveis.append(pai)

    return responsaveis


def gets_or_creates_responsaveis(responsaveis):
    """
    Retorna uma instância de Responsavel do banco de dados ou
    cria caso não exista.

    :param responsaveis:
    :return:
    """
    responsaveis_base = []

    for r in responsaveis:
        responsaveis_base.append(gets_or_creates_responsavel(r))

    return responsaveis_base


def gets_or_creates_responsavel(responsavel):
    try:
        responsavel_base = Responsavel.objects.get(
            nome=responsavel.nome,
            escola=responsavel.escola
        )
    except Responsavel.objects.model.DoesNotExist:
        username = gera_username(responsavel.nome)
        responsavel_base = Responsavel.create_profile(
            Responsavel, username, DEFAULT_PASSWORD, responsavel.nome, ''
        )
        responsavel_base.escola = responsavel.escola
        responsavel_base.email = responsavel.email
        responsavel_base.cpf = responsavel.cpf
        responsavel_base.telefone = responsavel.telefone
        responsavel_base.save()

    return responsavel_base


def gets_or_creates_aluno(aluno):
    """
    Retorna uma instância de Aluno do banco de dados ou
    cria caso não exista.

    :param aluno:
    :return:
    """
    try:
        aluno_base = Aluno.objects.get(
            nome=aluno.nome,
            matricula=aluno.matricula
        )
    except Aluno.objects.model.DoesNotExist:
        username = gera_username(aluno.nome)
        aluno_base = Aluno.create_profile(
            Aluno, username, DEFAULT_PASSWORD, aluno.nome, ''
        )
        aluno_base.escola = aluno.escola
        aluno_base.data_nascimento = aluno.data_nascimento
        aluno_base.matricula = aluno.matricula
        aluno_base.codigo_inep = aluno.codigo_inep
        #aluno_base.nome_social = aluno.nome_social
        aluno_base.save()

    return aluno_base


def insert_alunos(alunos, turma):
    """
    Função responsável por realizar a inserção dos alunos na base um a um
    """
    for aluno, responsaveis in alunos:
        aluno.escola = turma.escola
        aluno_base = gets_or_creates_aluno(aluno)

        responsaveis[0].escola = turma.escola

        if len(responsaveis) > 1:
            responsaveis[1].escola = turma.escola

        responsaveis_base = gets_or_creates_responsaveis(responsaveis)

        aluno_base.responsaveis.add(*responsaveis_base)

        turma.alunos.add(aluno_base)
        turma.save()


def importa_dados_base(arquivo):
    """
    Main method da importação
    :param arquivo:
    :return:
    """
    logger.info('--> importa_dados_base')
    dados_csv = ler_csv(arquivo)

    sort_matrix(dados_csv)

    # Inicialização da turma com a primeira turma do .csv
    turma = cria_turma_escola_distrito(dados_csv[0])
    alunos = []

    for row in dados_csv:

        # Gets or creates a turma na linha da iteração atual
        turma_aux = cria_turma_escola_distrito(row)

        # Quando passar para uma outra turma, os alunos da anterior serão inseridos
        if turma_aux != turma:
            insert_alunos(alunos, turma)

            turma = turma_aux

            # Limpa a lista de alunos
            alunos.clear()

        # Adiciona o primeiro aluno de cada turma nova.
        # Trecho utilizado para resolução de bug
        aluno = cria_aluno(row)
        responsaveis = cria_responsaveis(row)

        alunos.append((aluno, responsaveis))

    # Ao sair do loop, como não haverá mais linha com turma para ser trocada e disparar o insert,
    # esse alunos ficarão pendentes a serem inseridos, logo, o insert terá que ser disparado aqui
    # fora também
    insert_alunos(alunos, turma)
    logger.info('<-- importa_dados_base')