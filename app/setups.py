from django.contrib.auth import get_user_model
from app.models import Aluno
from app.models import Responsavel
from app.models import Profile
from app.models import Professor
from app.models import Escola
from app.models import Turma
from datetime import datetime


DEFAULT_PASS = 'super123'


data = [
    {
        'nome': 'ANA FLAVIA SARAIVA DE OLIVEIRA',
        'matricula': '1683559-0',
        'nascimento': '30/08/2006',
        'username': 'ana.oliveira',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'ALICE SARAIVA MEDEIROS',
                'username': 'alice.medeiros'
            },
        'pai': {
                'nome': 'FABIO CESAR OLIVEIRA FILHO',
                'username': 'fabio.filho'
            }
    },
    {
        'nome': 'ANA MARIA PROCOPIO FLORES',
        'matricula': '1719837-2',
        'nascimento': '19/01/2007',
        'username': 'ana.flores',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'SHARON PROCOPIO DA SILVA FLORES',
                'username': 'sharon.flores'
            },
        'pai': {
                'nome': 'JOSUE DE AZEVEDO FLORES',
                'username': 'josue.flores'
            }
    },
    {
        'nome': 'ANDREZA TEIXEIRA DE SOUZA',
        'matricula': '1828265-2',
        'nascimento': '11/03/2006',
        'username': 'andreza.souza',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'AMARILDA TEIXEIRA DE SOUZA',
                'username': 'amarilda.souza'
            },
        'pai': {
                'nome': 'ALEX DE SOUZA',
                'username': 'alex.souza'
            }
    },
    {
        'nome': 'CLARA BEATRIZ DE SOUZA LIMA',
        'matricula': '1615675-7',
        'nascimento': '17/08/2006',
        'username': 'clara.lima',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'JOANA PINTO DE SOUZA',
                'username': 'joana.souza'
            },
        'pai': {
                'nome': 'JUCELINO CARDOSO DE LIMA',
                'username': 'jucelino.lima'
            }
    },
    {
        'nome': 'DAIANE MELO MONTEIRO',
        'matricula': '1685885-9',
        'nascimento': '19/11/2006',
        'username': 'daiane.monteiro',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'DARCLEY CHAGAS DANTAS MELO',
                'username': 'darcley.melo'
            },
        'pai': {
                'nome': 'EDNELSON DA SILVA MONTEIRO',
                'username': 'ednelson.monteiro'
            }
    },
    {
        'nome': 'EVELY ABRANTE DOS SANTOS',
        'matricula': '1766028-9',
        'nascimento': '13/12/2006',
        'username': 'evely.santos',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'RAQUEL DE LIMA ABRANTE',
                'username': 'raquel.abrante'
            },
        'pai': {
                'nome': 'ERIOMAR MARANJEIRO DOS SANTOS',
                'username': 'eriomar.santos'
            }
    },
    {
        'nome': 'FABIANA ESTEFANY DUARTE DOS SANTOS',
        'matricula': '1493964-9',
        'nascimento': '01/07/2004',
        'username': 'fabiana.santos',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'ESTER PERES DUARTE',
                'username': 'ester.duarte'
            },
        'pai': {
                'nome': 'FABIANO SILVA DOS SANTOS',
                'username': 'fabiano.santos'
            }
    },
    {
        'nome': 'FABIO DE SOUZA RODRIGUES',
        'matricula': '1102630-8',
        'nascimento': '08/05/2002',
        'username': 'fabio.rodrigues',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'ELIZABETE OLIVEIRA DE SOUZA',
                'username': 'elizabete.souza'
            },
        'pai': {
                'nome': 'RAIMUNDO NONATO DE SA RODRIGUES',
                'username': 'raimundo.rodrigues'
            }
    },
    {
        'nome': 'GIOVANNA BRANDAO DE ARAUJO',
        'matricula': '2138147-0',
        'nascimento': '08/04/2007',
        'username': 'giovanna.araujo',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'LUCILENE RIBEIRO BRANDAO',
                'username': 'lucilene.brandao'
            },
        'pai': {
                'nome': 'GILSON MOURAO DE ARAUJO',
                'username': 'gilson.araujo'
            }
    },
    {
        'nome': 'GUILHERME MENEZES ROSSY',
        'matricula': '1851817-6',
        'nascimento': '25/01/2006',
        'username': 'guilherme.rossy',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'EDNEIDE VASCONCELOS DE MENEZES',
                'username': 'edneide.menezes'
            },
        'pai': {
                'nome': 'DENIS SOUZA ROSSY',
                'username': 'denis.rossy'
            }
    },
    {
        'nome': 'IAGO SILVA DA SILVA',
        'matricula': '1653433-6',
        'nascimento': '20/03/2006',
        'username': 'iago.silva',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'EDILETE FERNANDES DA SILVA',
                'username': 'edilete.silva'
            },
        'pai': {
                'nome': 'EVERALDO GUERRA DA SILVA',
                'username': 'everaldo.silva'
            }
    },
    {
        'nome': 'ITARO VIEIRA JUCA',
        'matricula': '1702056-5',
        'nascimento': '18/11/2006',
        'username': 'itaro.juca',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'JULIMAR DOS SANTOS VIEIRA GARCIA',
                'username': 'julimar.garcia'
            },
        'pai': {
                'nome': 'SILVESTRE MOREIRA JUCA',
                'username': 'silvestre.juca'
            }
    },
    {
        'nome': 'JOAO VITOR FERREIRA BORGES',
        'matricula': '2189364-0',
        'nascimento': '27/12/2006',
        'username': 'joao.borges',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'CLAUDIA VALERIA BARROS FERREIRA',
                'username': 'claudia.ferreira'
            },
        'pai': {
                'nome': 'MARLON MOREIRA BORGES',
                'username': 'marlon.borges'
            }
    },
    {
        'nome': 'LETICIA LIMA DE OLIVEIRA',
        'matricula': '1570816-0',
        'nascimento': '06/02/2006',
        'username': 'leticia.oliveira',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'LUCILENE DA SILVA LIMA',
                'username': 'lucilene.lima'
            },
        'pai': {
                'nome': 'LUIZ DA CSILVA DE OLIVEIRA',
                'username': 'luiz.oliveira'
            }
    },
    {
        'nome': 'MARCELA NASCIMENTO LIMA',
        'matricula': '2241867-9',
        'nascimento': '21/10/2006',
        'username': 'marcela.lima',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'SUELEN CRISTINA BRAGA DO NASCIMENTO',
                'username': 'suelem.nascimento'
            },
        'pai': {
                'nome': 'MARCIO JOSE DA SILVA LIMA',
                'username': 'marcio.lima'
            }
    },
    {
        'nome': 'NATHALIA GONCALVES DA SILVA',
        'matricula': '1574567-8',
        'nascimento': '10/09/2005',
        'username': 'nathalia.silva',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'MARTA DA SILVA GONCLAVES',
                'username': 'marta.gonclaves'
            },
        'pai': {
                'nome': 'CARLOS FIRMINO DA SILVA',
                'username': 'carlos.silva'
            }
    },
    {
        'nome': 'ORLEILSON LIRA HORREDA',
        'matricula': '1753974-9',
        'nascimento': '24/12/2004',
        'username': 'orleilson.horreda',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'ANGELA LIRA ALVES',
                'username': 'angela.alves'
            },
        'pai': {
                'nome': 'RAYSON RAMOS HORREDA',
                'username': 'rayson.horreda'
            }
    },
    {
        'nome': 'PABLO SAMPAIO DOS ANJOS',
        'matricula': '1932304-2',
        'nascimento': '07/02/2007',
        'username': 'pablo.anjos',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'ALCIONE SAMPAIO LIMA',
                'username': 'alcione.lima'
            },
        'pai': {
                'nome': 'ANTONIO CARLOS DOS ANJOSDA SILVA',
                'username': 'antonio.silva'
            }
    },
    {
        'nome': 'PAMELA SANTOS DA SILVA',
        'matricula': '1827557-5',
        'nascimento': '08/11/2006',
        'username': 'pamela.silva',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'MARCELA SOUZA DOS SANTOS',
                'username': 'marcela.santos'
            },
        'pai': {
                'nome': 'MEDSON ANDRADE DA SILVA',
                'username': 'medson.silva'
            }
    },
    {
        'nome': 'PEDRO ELIAS CANIZO TORRES',
        'matricula': '1698125-1',
        'nascimento': '20/12/2006',
        'username': 'pedro.elias',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'MARINETE CANIZO TORRES',
                'username': 'marinte.torres'
            },
        'pai': {
                'nome': 'JOSE ELIAS DE LIMA TORRES',
                'username': 'jose.torres'
            }
    },
    {
        'nome': 'RAYRES TEIXEIRA DA SILVA',
        'matricula': '2216479-0',
        'nascimento': '30/03/2005',
        'username': 'rayres.silva',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'JANE TEIXEIRA DA SILVA',
                'username': 'jane.silva'
            },
        'pai': None
    },
    {
        'nome': 'RAYSSA ANDRADE MOTA',
        'matricula': '1702246-0',
        'nascimento': '15/02/2007',
        'username': 'rayssa.mota',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'RIANNY ANDRADE MOTA',
                'username': 'rianny.mota'
            },
        'pai': None
    },
    {
        'nome': 'RENATA VITORIA BRAGA DE LIMA',
        'matricula': '2127702-8',
        'nascimento': '04/07/2006',
        'username': 'renata.lima',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'ELISANGELA DA SILVA BRAGA',
                'username': 'elisangela.braga'
            },
        'pai': {
                'nome': 'FRANCISCO DA SILVA LIMA',
                'username': 'francisca.lima'
            }
    },
    {
        'nome': 'RUTH LETICIA MARINHO DOS SANTOS',
        'matricula': '1752204-8',
        'nascimento': '14/03/2007',
        'username': 'ruth.santos',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'LUIMAR MARINHO MEIRELES',
                'username': 'luimar.meireles'
            },
        'pai': {
                'nome': 'CARLOS DE JESUS BARROSO DOS SANTOS',
                'username': 'carlos.santos'
            }
    },
    {
        'nome': 'SILAS EDUARDO MARAES SOUZA',
        'matricula': '1700285-0',
        'nascimento': '25/12/2006',
        'username': 'silas.souza',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'EDIVANIA MESQUITA MARAES',
                'username': 'edivania.maraes'
            },
        'pai': {
                'nome': 'SILAS DE JESUS VILAGELIM',
                'username': 'silas.vilagelim'
            }
    },
    {
        'nome': 'SOFIA SOUZA DE SOUZA',
        'matricula': '1956713-8',
        'nascimento': '31/07/2006',
        'username': 'sofia.souza',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'ERICA SILVA DE SOUZA',
                'username': 'erica.souza'
            },
        'pai': {
                'nome': 'SEBASTIAO GOMES DE SOUZA',
                'username': 'sebastiao.souza'
            }
    },
    {
        'nome': 'TIAGO SOARES QUEIROZ',
        'matricula': '1489739-3',
        'nascimento': '21/07/2004',
        'username': 'tiago.queiroz',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'DANIELA SOARES QUEIROZ',
                'username': 'daniela.queiroz'
            },
        'pai': None
    },
    {
        'nome': 'VICTOR JUNIOR MUNIZ SALDANHA',
        'matricula': '1933963-1',
        'nascimento': '01/01/2007',
        'username': 'victor.saldanha',
        'genero': Profile.MASCULINO,
        'mae': {
                'nome': 'SILVIANE FIALHO MUNIZ',
                'username': 'silviane.muniz'
            },
        'pai': {
                'nome': 'GIDEONE PEREIRA SALDANHA',
                'username': 'gideone.saldanha'
            }
    },
    {
        'nome': 'YASMIN CORREIA DE MEDEIROS',
        'matricula': '1580821-1',
        'nascimento': '06/12/2005',
        'username': 'yasmin.medeiros',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'DEISE CORREIA DE MEDEIROS',
                'username': 'deise.medeiros'
            },
        'pai': None
    },
    {
        'nome': 'ZILANE ROCHA DE OLIVEIRA',
        'matricula': '1613868-6',
        'nascimento': '21/01/2006',
        'username': 'zilane.oliveira',
        'genero': Profile.FEMININO,
        'mae': {
                'nome': 'DELANE ROCHA CELESTINO',
                'username': 'delane.celestino'
            },
        'pai': {
                'nome': 'ZILMAR CHAVES DE OLIVEIRA',
                'username': 'zilmar.oliveira'
            }
    },
]

data_professores = [
    {
        'nome': 'ANA CASSIA NASCIMENTO ROSAS',
        'matricula': '98.105918-1A',
        'funcao': 'PROFESSOR 1º AO 5º ANO',
        'username': 'ana.rosas'
    },
    {
        'nome': 'ANA CLAUDIA ELIAS TEIXEIRA',
        'matricula': '98.116366-3A',
        'funcao': 'PROF PRE-ESCOLA (1-5 ANOS)',
        'username': 'ana.teixeira'
    },
    {
        'nome': 'ANDREZA CRISTIANE MELO DO LAGO',
        'matricula': '98.127604-2A',
        'funcao': 'PROFESSOR 1º AO 5º ANO',
        'username': 'andreza.lago'
    },
    {
        'nome': 'AUGUSTO LUSO RIBEIRO JUNIOR',
        'matricula': '98.104699-3A',
        'funcao': 'AUX. BIBLIOTECA',
        'username': 'augusto.junior'
    },
    {
        'nome': 'BRUNO LIMA DE ALMEIDA',
        'matricula': '98.121367-9A',
        'funcao': 'ASSISTENTE ADMINISTRATIVO',
        'username': 'bruno.almeida'
    },
    {
        'nome': 'DANIELLE SILVEIRA LIMA',
        'matricula': '98.127206-3A',
        'funcao': 'PROFESSOR 1º AO 5º ANO',
        'username': 'danielle.lima'
    },
    {
        'nome': 'EDNEIDE VASCONCELOS DE MENEZES',
        'matricula': '98.104091-0A',
        'funcao': 'AUX. BIBLIOTECA',
        'username': 'edineide.menezes'
    },
    {
        'nome': 'EVYLA KATIUCIA NUNES SOUZA',
        'matricula': '98.122006-3A',
        'funcao': 'PROFESSOR REFORÇO ESCOLAR',
        'username': 'evyla.souza'
    },
    {
        'nome': 'FLAVIA MARA DOS SANTOS BERNARDO',
        'matricula': '98.106197-6A',
        'funcao': 'PROFESSOR 1º AO 5º ANO',
        'username': 'flavia.bernardo'
    },
    {
        'nome': 'FRANCISCA FELISBELA SILVA SENA',
        'matricula': '98.100782-3B',
        'funcao': 'PROFESSOR 1º AO 5º ANO',
        'username': 'francisca.sena'
    },
    {
        'nome': 'GRACY MACHADO MONTE',
        'matricula': '98.065316-0A',
        'funcao': 'ODONTOLOGO',
        'username': 'gracy.monte'
    },
    {
        'nome': 'KAREN RALLINE DA CUNHA E SILVA',
        'matricula': '98.103757-9A/B',
        'funcao': 'COORDENADOR TELECENTRO',
        'username': 'karen.silva'
    },
    {
        'nome': 'KATHELEEN SANTOS RODRIGUES',
        'matricula': '98.121776-3A',
        'funcao': 'ASSISTENTE ADMINISTRATIVO',
        'username': 'katheleen.rodrigues'
    },
    {
        'nome': 'LUZIENE ALMEIDA CHAVES DO VALE',
        'matricula': '98.121634-1A',
        'funcao': 'TUTOR IAS (AIRTON SENA)',
        'username': 'luziene.vale'
    },
    {
        'nome': 'MANUEL PORTO GALVAO',
        'matricula': '98.104730-2A',
        'funcao': 'PROFESSOR ED. FISICA 1º AO 5º ANO',
        'username': 'manuel.galvao'
    },
    {
        'nome': 'MARCIA CRISTINA SALLES BOTELHO',
        'matricula': '98.115403-6A',
        'funcao': 'PROFESSOR 1º AO 5º ANO',
        'username': 'marcia.botelho'
    },
    {
        'nome': 'MARIA DE LOURDES AZEVEDO BARBOSA',
        'matricula': '98.097636-9B',
        'funcao': 'PROF PRE-ESCOLA (1-5 ANOS)',
        'username': 'maria.barbosa'
    },
    {
        'nome': 'MARILUCE DINIZ NUNES',
        'matricula': '98.105308-6A',
        'funcao': 'APOIO ADMINSTRATIVO',
        'username': 'mariluce.nunes'
    },
    {
        'nome': 'MARINETE DA SILVA COSTA',
        'matricula': '98.013794-4A',
        'funcao': 'AGENTE DE PORTARIA',
        'username': 'marinete.costa'
    },
    {
        'nome': 'REGEANE RAMOS CHAVES',
        'matricula': '98.115008-1A',
        'funcao': 'DIRETOR DE ESCOLA',
        'username': 'regeane.chaves'
    },
    {
        'nome': 'RONALDO CESAR MARQUES DA COSTA',
        'matricula': '98.072422-0B',
        'funcao': 'AUX. SERVIÇOS GERAIS',
        'username': 'ronaldo.costa'
    },
    {
        'nome': 'SAMIAN FREITAS RODRIGUES',
        'matricula': '98.097123-5B',
        'funcao': 'AGENTE DE SAÚDE',
        'username': 'samian.rodrigues'
    },
    {
        'nome': 'SHEILA PONTES DE SOUZA ROCCO',
        'matricula': '98.124376-4A',
        'funcao': 'PROFESSOR 1º AO 5º ANO',
        'username': 'sheila.rocco'
    },
    {
        'nome': 'SIRLENE DA SILVA SOLIMOES',
        'matricula': '98.076174-5B/E',
        'funcao': 'PROFESSOR 1º AO 5º ANO/PEDAGOGO',
        'username': 'sirlene.solimoes'
    },
    {
        'nome': 'WANKERLENE NOGUEIRA GUIMARAES',
        'matricula': '98.067258-0B',
        'funcao': 'PROF PRE-ESCOLA (1-5 ANOS)',
        'username': 'wankerlene.guimaraes'
    }
]


def create_responsavel(nome, username):
    user = get_user_model()(username=username)
    user.set_password(DEFAULT_PASS)
    user.save()

    resp = Responsavel(nome=nome, user=user)
    resp.role = Profile.RESPOSIBLE
    resp.save()
    return resp


def create_aluno_ex(
        turma, nome, username, genero, data_nascimento, matricula,
        mae=None, pai=None):
    user = get_user_model()(username=username)
    user.set_password(DEFAULT_PASS)
    user.save()

    aluno = Aluno(nome=nome, user=user)
    aluno.role = Profile.STUDENT
    aluno.genero = genero
    aluno.matricula = matricula
    aluno.data_nascimento = data_nascimento
    aluno.save()

    if mae is not None:
        aluno.responsaveis.add(mae)

    if pai is not None:
        aluno.responsaveis.add(pai)

    aluno.save()
    turma.alunos.add(aluno)
    turma.save()

    return aluno


def create_professor(escola, nome, username, matricula, funcao):
    user = get_user_model()(username=username)
    user.set_password(DEFAULT_PASS)
    user.save()

    p = Professor(nome=nome, user=user)
    p.role = Profile.PROFESSOR
    p.matricula = matricula
    p.funcao = funcao
    p.save()
    p.escola.add(escola)
    p.save()

    return p


def parse_data(turma, data):
    for d in data:
        birthday = datetime.strptime(d['nascimento'], '%d/%m/%Y')
        mae = create_responsavel(
            d['mae']['nome'],
            d['mae']['username']
        )

        pai = None

        if d['pai'] is not None:
            pai = create_responsavel(
                d['pai']['nome'],
                d['pai']['username']
            )

        create_aluno_ex(
            turma,
            d['nome'],
            d['username'],
            d['genero'],
            birthday,
            d['matricula'],
            mae,
            pai)


def parse_professor_data(escola, data):
    for d in data:
        create_professor(
            escola,
            d['nome'],
            d['username'],
            d['matricula'],
            d['funcao'])


def create_escola_super_ensino():
    escola = Escola(nome='Escola Super Ensino')
    escola.save()

    turma = Turma(
        identificador='5o. Ano A', descricao='', escola=escola, serie=5,
        status=Turma.ATIVA)
    turma.save()

    # Criando professores ...
    prof_pardal = create_professor(
        escola, 'Prof. Pardal', 'pardal', '', '')
    prof_ludovico = create_professor(
        escola, 'Prof. Ludovico', 'ludovico', '', '')

    # Criar responsável
    margarida = create_responsavel('Margarida', 'margarida')
    donald = create_responsavel('Pato Donald', 'pato.donald')

    birthday = datetime.strptime('30/08/2006', '%d/%m/%Y')

    # Alunos
    huguinho = create_aluno_ex(
            turma, 'Huguinho', 'huguinho', Profile.MASCULINO, birthday,
            '', margarida, donald)

    zezinho = create_aluno_ex(
            turma, 'Zezinho', 'zezinho', Profile.MASCULINO, birthday,
            '', margarida, donald)

    luizinho = create_aluno_ex(
            turma, 'Luizinho', 'luizinho', Profile.MASCULINO, birthday,
            '', margarida, donald)

    turma.alunos.add(huguinho)
    turma.alunos.add(zezinho)
    turma.alunos.add(luizinho)

    turma.professores.add(prof_pardal)
    turma.professores.add(prof_ludovico)
    turma.save()
