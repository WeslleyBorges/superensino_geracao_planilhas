class AlunoDTO(object):
    def __init__(self, id, nome, imagem, serie):
        self.id = id
        self.nome = nome
        self.imagem = imagem
        self.serie = serie


class AulasTimestampDTO(object):
    def __init__(self, assunto, timestamp):
        self.assunto = assunto
        self.timestamp = timestamp


class DisciplinaAulasDTO(object):
    def __init__(self, id, disciplina, aulas):
        self.id = id
        self.disciplina = disciplina
        self.aulas = aulas


class SuperPaiExercicioDTO(object):
    def __init__(self, disciplina, nome, data, timestamp, erros, acertos):
        self.disciplina = disciplina
        self.nome = nome
        self.data = data
        self.timestamp = timestamp
        self.erros = erros
        self.acertos = acertos


class SuperPaiDisciplinaStatusDTO(object):
    def __init__(self, disciplina, erros, acertos):
        self.disciplina = disciplina
        self.erros = erros
        self.acertos = acertos
