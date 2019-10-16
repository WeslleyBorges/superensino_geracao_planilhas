from django.http import HttpResponse
import pdfkit
import os
from PyPDF2 import PdfFileMerger, PdfFileReader
from zipfile import ZipFile, ZIP_DEFLATED
from django.core.mail import send_mail
from django_boto.s3 import upload
try:
    import importlib
    dj_sett_module = os.environ['DJANGO_SETTINGS_MODULE']
    settings = importlib.import_module(dj_sett_module, 'superensinopro.settings')
    FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
except ImportError:
    FROM_EMAIL = 'services@appsuperensino.com.br'
import subprocess
from pdfkit.configuration import Configuration
from sys import getrecursionlimit, setrecursionlimit

# Current Working Directory
CWD = os.getcwd()
# Diretório raiz tmp, onde estará o .zip, diretórios com os arquivos html e pdf
TEMP = '%s/app/tmp/' % CWD
# Diretório onde estarão as páginas html a serem renderizadas no PDF
TEMP_HTML_FILES_DIR = '%s/app/tmp/html-tmp/' % CWD
# Diretório no qual serão armazenados os PDFs gerados
TEMP_PDF_FILES_DIR = '%s/app/tmp/pdf-tmp/' % CWD


class AlunoRespUser:
    def __init__(self, **kwargs):
        self.pk = kwargs['id']
        self.nome = kwargs['nome']
        self.matricula = kwargs['matricula']
        self.responsavel1_username = kwargs['responsaveis'][0]['username']
        self.responsavel2_username = kwargs['responsaveis'][1]['username']
        self.escola_nome = kwargs['escola_nome']
        self.escola_slug = kwargs['escola_slug']
        self.serie = kwargs['serie']
        self.turno = kwargs['turno']
        self.turma_letra = kwargs['turma_letra']
        self.username = kwargs['aluno_username']


def deserialize_aluno_queryset(data):

    alunos = []

    for datum in data:
        aluno = AlunoRespUser(**datum)
        alunos.append(aluno)

    return alunos


def merge_pdf_files(nome_escola):

    file_list = os.listdir(TEMP_PDF_FILES_DIR)
    file_list.sort()
    pdf_files = [f for f in file_list if f.endswith("pdf")]
    merger = PdfFileMerger()

    for filename in pdf_files:
        merger.append(PdfFileReader(os.path.join(TEMP_PDF_FILES_DIR, filename), "rb"))

    merger.write(os.path.join(TEMP_PDF_FILES_DIR, nome_escola + '.pdf'))


def get_nome_escola(nome_escola):
    """
    Considerando que o nome de todas as escolas que terão a cartinha gerada
    inicia com 'E.M.', serão considerados os dois nomes após 'E.M.'
    :param nome_escola:
    :return:
    """
    nome_escola_simplificado = []

    sobrenomes_nao_significativos = ['de', 'do', 'dos', 'da', 'das', 'e']

    for nome in nome_escola.split(' '):
        if len(nome_escola_simplificado) == 3:
            break
        if nome.lower() not in sobrenomes_nao_significativos:
            nome_escola_simplificado.append(nome)

    return ' '.join(nome_escola_simplificado)


def school_name_builder(aluno):
    escola = get_nome_escola(aluno.escola_nome)
    serie = aluno.serie
    turma = aluno.turma_letra
    turno = aluno.turno

    return '%s - %s - %s - %s' % (escola, serie, turma, turno)


def get_nome_aluno(aluno):
    nomes = []
    sobrenomes_nao_significativos = ['de', 'do', 'dos', 'da', 'das', 'e']

    for nome in aluno.nome.split(' '):
        if len(nomes) == 3:
            break
        if nome.lower() not in sobrenomes_nao_significativos:
            nomes.append(nome)

    return ' '.join(nomes)


def clean_temp_dirs(root_path):
    for file in os.listdir(root_path):
        file_path = os.path.join(root_path, file)

        if os.path.isfile(file_path) and not file_path.endswith('.oculto'):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            clean_temp_dirs(file_path)


def get_data(aluno):
    """
    Obtém do banco de dados os dados de login do aluno e de seus responsáveis
    :param aluno:
    :return: Dictionary com os dados de login
    """
    data = {'nome_aluno': get_nome_aluno(aluno),
            'user_aluno': aluno.username,
            'login_resp1': aluno.responsavel1_username,
            'login_resp2': aluno.responsavel2_username,
            'escola': school_name_builder(aluno),
            'senha': '123mudar'}

    return data


def replace_html_shown_data(aluno):
    """
    Substitui
    :param aluno:
    :return: O caminho completo do HTML utilizado para geração do PDF
             e o próprio PDF
    """
    # Caminho do template que será utilizado para construir as páginas HTML de cada aluno
    # Serve somente para armazenar a estrutura da página a ser renderizada no PDF
    template_path = 'app/templates/app/carta_dados.html'
    # Caminho para o background da página
    static_background = '../../static/img/background.png'

    # Abertura do HTML modelo
    html_base = open(template_path, 'r')

    # Leitura do conteúdo da página HTML como string
    html_file_string_content = html_base.read()

    # Fechamento do arquivo
    html_base.close()

    # Obtenção dos dados de login do banco
    data = get_data(aluno)

    # Substituição dos marcadores inseridos na página pelos dados obtidos
    # Aqui rolou uma bela de uma POG. Esperava poder passar um dictionary context para a página ;_;
    html_file_string_content = html_file_string_content.replace('ESCOLA', data['escola'])
    html_file_string_content = html_file_string_content.replace('NOME_ALUNO', data['nome_aluno'])
    html_file_string_content = html_file_string_content.replace('LOGIN_ALUNO', data['user_aluno'])
    html_file_string_content = html_file_string_content.replace('SENHA_ALUNO', data['senha'])
    html_file_string_content = html_file_string_content.replace('LOGIN_MAE', data['login_resp1'])
    html_file_string_content = html_file_string_content.replace('LOGIN_PAI', data['login_resp2'])
    html_file_string_content = html_file_string_content.replace('SENHA_RESPONSAVEL', data['senha'])
    html_file_string_content = html_file_string_content.replace('STATIC_BACKGROUND', static_background)

    # Nome do arquivo que será criado para cada aluno
    # Será substituído em breve pelo nome da escola onde irá conter as páginas de todos os alunos
    # da escola
    nome_aluno_arquivo = '%s-%s-%s-%s' % (aluno.serie, aluno.turma_letra, '-'.join(aluno.nome.split(' ')),
                                       aluno.matricula.replace(' ', ''))

    # Montagem do caminho do HTML gerado
    arquivo_html_path = TEMP_HTML_FILES_DIR
    arquivo_html_path += nome_aluno_arquivo
    arquivo_html_path += '.html'

    # Montagem do caminho do PDF gerado
    arquivo_pdf_path = TEMP_PDF_FILES_DIR
    arquivo_pdf_path += nome_aluno_arquivo
    arquivo_pdf_path += '.pdf'

    # Criação de um novo arquivo para o aluno
    new_file = open(arquivo_html_path, 'w+')

    # Escrita no arquivo com todos os marcadores já substituídos
    new_file.write(html_file_string_content)

    # Fechamento do arquivo
    new_file.close()

    # Retorno da tula: caminho do html e do pdf
    return arquivo_html_path, arquivo_pdf_path


def zip_pdf(nome_escola):
    zf = ZipFile("%s%s.zip" % (TEMP, nome_escola), "w", ZIP_DEFLATED)

    abs_src = os.path.abspath(TEMP_PDF_FILES_DIR)

    for dirname, subdirs, files in os.walk(TEMP_PDF_FILES_DIR):
        for filename in files:
            if filename.find(nome_escola) != -1 and not filename.endswith('.oculto'):
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
    zf.close()


def upload_and_generate_url(nome_escola):
    filename = '%s%s.zip' % (TEMP, nome_escola)
    name = nome_escola + '.zip'
    download_url = upload(filename=filename, name=name)
    return download_url


def send_link(url, user_email, nome_escola):
    send_mail(
        'Cartas com credenciais dos alunos e responsáveis - %s' % nome_escola,
        url,
        from_email=FROM_EMAIL,
        recipient_list=[user_email]
    )


def emite_pdf(merger, options, configuration, nome_escola, queryset):
    try:
        aluno = queryset[0]
    except IndexError:
        merger.write(os.path.join(TEMP_PDF_FILES_DIR, nome_escola + '.pdf'))
        return

    file_path = replace_html_shown_data(aluno)

    pdfkit.from_file(file_path[0], file_path[1], options=options, configuration=configuration)

    os.remove(file_path[0])

    merger.append(PdfFileReader(file_path[1], "rb"))

    os.remove(file_path[1])

    emite_pdf(merger, options, configuration, nome_escola, queryset[1:])


def gerar_carta(user_email, data):
    """
    Main method da rotina
    :param request:
    :param queryset:
    :return:
    """
    # Deserialização da lista de alunos
    alunos = deserialize_aluno_queryset(data)

    nome_escola = alunos[0].escola_nome
    slug_escola = alunos[0].escola_slug

    configuration = None

    if 'DYNO' in os.environ:
        wk_process = subprocess.Popen(['which', 'bin/wkhtmltopdf'], stdout=subprocess.PIPE).communicate()[0].strip()

        configuration = Configuration(wkhtmltopdf=wk_process)

    merger = PdfFileMerger()

    options = {
        'page-size': 'A5',
    }

    max_recursion_depth = getrecursionlimit()

    setrecursionlimit(2000)

    emite_pdf(merger, options, configuration, slug_escola, alunos)

    setrecursionlimit(max_recursion_depth)

    # Zip do diretório que conterá os PDFs
    zip_pdf(slug_escola)

    url = upload_and_generate_url(slug_escola)

    user_email = user_email

    send_link(url, user_email, nome_escola)

    clean_temp_dirs(TEMP)
