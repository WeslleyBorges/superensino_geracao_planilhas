"""
Script auxiliar para preencher o banco de questões para fins de teste.
"""
from app.models import Disciplina, Aula, Exercicio, Alternativa, Attachment


series = [5,6,7,8,9]
series_prova_brasil = [5,9]
bimestres = [1,2,3,4]

def populate():
    print("Criando as disciplinas básicas...")
    portugues = Disciplina.create("Português")
    matemática = Disciplina.create("Matemática")
    historia = Disciplina.create("História")
    geografia = Disciplina.create("Geografia")
    ciencias = Disciplina.create("Ciências")

    print("Criando as disciplinas para Prova Brasil...")
    portugues_prova_brasil = Disciplina.create("Português", True)
    matemática_prova_brasil = Disciplina.create("Matemática", True)

    disciplinas = [
        portugues, matemática,historia,geografia,ciencias
    ]

    disciplinas_prova_brasil = [
        portugues_prova_brasil, matemática_prova_brasil
    ]

    print("Início do loop de questões do super reforço...")
    for disciplina in disciplinas:
        for serie in series:
            for bim in bimestres:
                for index in range(5):
                    aula = Aula.create(
                        disciplina,
                        "Assunto_{0}{1}{2}{3}".format(disciplina.nome, serie, bim, index),
                        serie,
                        bim
                    )
                    Attachment.create(aula, 'http://localhost.com/v', '')

                    for ex in range(5):
                        exercicio = Exercicio.create(aula, "Aula {0}_{1}".format(aula.assunto, ex))

                        Alternativa.create(exercicio, 'enunciado', '', True)
                        Alternativa.create(exercicio, 'enunciado', '', False)
                        Alternativa.create(exercicio, 'enunciado', '', False)
                        Alternativa.create(exercicio, 'enunciado', '', False)

                        print('.')

    print("Início do loop de questões da prova brasil...")
    for disciplina in disciplinas_prova_brasil:
        for serie in series:
            for index in range(5):
                aula = Aula.create(
                    disciplina,
                    "Assunto_{0}{1}{2}{3}".format(disciplina.nome, serie, 1, index),
                    serie,
                    1
                )
                Attachment.create(aula, 'http://localhost.com/v', '')
                for ex in range(5):
                    exercicio = Exercicio.create(aula, "Aula {0}_{1}".format(aula.assunto, ex))

                    Alternativa.create(exercicio, 'enunciado', '', True)
                    Alternativa.create(exercicio, 'enunciado', '', False)
                    Alternativa.create(exercicio, 'enunciado', '', False)
                    Alternativa.create(exercicio, 'enunciado', '', False)

                    print('.')
