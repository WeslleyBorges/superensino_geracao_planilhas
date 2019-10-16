from datetime import datetime
from random import randint

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from lxml import html

from app.managers import AlunoQuerySet, ProfessorQuerySet
from app.managers import AttachmentQuerySet
from app.managers import DisciplinaQuerySet
from app.managers import EscolaQuerySet, ResponsavelQuerySet, TurmaQuerySet, GestorQuerySet
from app.managers import ExercicioQuerySet
from app.managers import HistoricoAulasAssistidasQuerySet
from app.managers import RespostaQuerySet
from easy_thumbnails.fields import ThumbnailerImageField


def _gera_token_aluno():
    token = ''

    for i in range(8):
        rand_digit = str(randint(0, 9))
        token += rand_digit

    if not Aluno.objects.filter(token=token):
        return token

    _gera_token_aluno()


def enum(*sequential, **named):
    """C# enum style for python 3.x."""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


series_enum = enum(
    debug=0,
    ano_1_fundamental=1,
    ano_2_fundamental=2,
    ano_3_fundamental=3,
    ano_4_fundamental=4,
    ano_5_fundamental=5,
    ano_6_fundamental=6,
    ano_7_fundamental=7,
    ano_8_fundamental=8,
    ano_9_fundamental=9,
    )

bimestre_enum = enum(
    bim_1=1,
    bim_2=2,
    bim_3=3,
    bim_4=4,
)

attach_type_enum = enum(
    youtube_link=1,
)

classificacao_enum = enum(
    classificacao_1=1,
    classificacao_2=2,
    classificacao_3=3,
    classificacao_4=4,
)

SERIES_CHOICES = (
    (series_enum.debug, "Debug"),
    (series_enum.ano_1_fundamental, "1o. Ano [Fundamental]"),
    (series_enum.ano_2_fundamental, "2o. Ano [Fundamental]"),
    (series_enum.ano_3_fundamental, "3o. Ano [Fundamental]"),
    (series_enum.ano_4_fundamental, "4o. Ano [Fundamental]"),
    (series_enum.ano_5_fundamental, "5o. Ano [Fundamental]"),
    (series_enum.ano_6_fundamental, "6o. Ano [Fundamental]"),
    (series_enum.ano_7_fundamental, "7o. Ano [Fundamental]"),
    (series_enum.ano_8_fundamental, "8o. Ano [Fundamental]"),
    (series_enum.ano_9_fundamental, "9o. Ano [Fundamental]"),
)

BIMESTRE_CHOICES = (
    (bimestre_enum.bim_1, "1o. Bimestre"),
    (bimestre_enum.bim_2, "2o. Bimestre"),
    (bimestre_enum.bim_3, "3o. Bimestre"),
    (bimestre_enum.bim_4, "4o. Bimestre"),
)

CLASSIFICACAO_CHOICES = (
    (classificacao_enum.classificacao_1, "C1"),
    (classificacao_enum.classificacao_2, "C2"),
    (classificacao_enum.classificacao_3, "C3"),
    (classificacao_enum.classificacao_4, "C4"),
)

ATTACH_TYPE_CHOICE = (
    (attach_type_enum.youtube_link, 'You Tube Link'),
)

turno_enum = enum(
    matutino='MAT',
    vespertino='VESP'
)
TURNO_CHOICE = (
    (turno_enum.matutino, 'MAT'),
    (turno_enum.vespertino, 'VESP'),
)


class Profile(models.Model):
    # Gênero
    MASCULINO = 1
    FEMININO = 2

    # Papel
    UNKNOWN = 0
    ADMINISTRATOR = 1
    ASSISTANT_PROFESSOR = 2
    STUDENT = 3
    PROFESSOR = 4
    SUPERVISOR = 5
    RESPOSIBLE = 6
    GESTOR_ESCOLAR = 7
    SUPER_ENSINO_USER = 8

    ROLE_CHOICES = (
        (ADMINISTRATOR, 'Administrador'),
        (ASSISTANT_PROFESSOR, 'Professor Assistente'),
        (STUDENT, 'Aluno'),
        (PROFESSOR, 'Professor'),
        (SUPERVISOR, 'Supervisor'),
        (RESPOSIBLE, 'Responsável'),
        (GESTOR_ESCOLAR, 'Gestor Escolar'),
        (SUPER_ENSINO_USER, 'Super Ensino User'),
    )

    GENERO_OPCOES = (
        (MASCULINO, 'Masculino'),
        (FEMININO, 'Feminino'),
    )

    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, null=True, blank=True)
    genero = models.PositiveSmallIntegerField(
        choices=GENERO_OPCOES, default=MASCULINO, null=True, blank=True)
    imagem = ThumbnailerImageField(
        upload_to='profile/%Y/%m/%d/', blank=True, null=True, default='static/img/default_avatar_male.jpg'
    )

    @classmethod
    def create_profile(cls, baseclass, username, password, nome, email):
        """Cria um novo perfil de usuário no sistema

        O perfil do usário é definido pelo valor de role e do tipo da class
        passado em baseclass.

        Ex: Para criar um novo perfil de aluno
            novo_aluno = Aluno.create_profile(Aluno, ...)
        """
        user = get_user_model()()
        user.username = username
        user.set_password(password)
        user.email = email
        user.save()

        if type(baseclass) is Aluno:
            role = cls.STUDENT
        elif type(baseclass) is Responsavel:
            role = cls.RESPOSIBLE
        elif type(baseclass) is Professor:
            role = cls.PROFESSOR
        elif type(baseclass) is Gestor:
            role = cls.GESTOR_ESCOLAR
        else:
            role = cls.UNKNOWN

        instance = baseclass(user=user, nome=nome, role=role)
        instance.save()
        return instance

    def __str__(self):
        return self.user.username

    def get_username(self):
        if self.user is not None:
            return self.user.username
        return ''

    def get_baseclass(self):
        string_class = [v for k,v in self.ROLE_CHOICES if k == self.role][0]
        if string_class=='Gestor Escolar':
            string_class='Gestor'
        if string_class=='Responsável':
            string_class='Responsavel'
        return eval(string_class).objects.get(user=self.user)


class Administrador(Profile):
    nome = models.CharField(max_length=80)

    def __str__(self):
        return self.nome


class Gestor(Profile):
    nome = models.CharField(max_length=80)

    objects = GestorQuerySet.as_manager()

    def get_escolas_json(self, distrito=None, bairro=None):
        data = []
        filters = {}

        if distrito is not None:
            filters['distrito_id'] = distrito

        if bairro is not None:
            filters['endereco__bairro'] = bairro
        for esc in self.escola_set.filter(**filters):
            esc_dict = {
                'id': esc.id,
                'nome': esc.nome,
                'slug': esc.slug
            }
            data.append(esc_dict)
        return data

    def __str__(self):
        return self.nome


class SuperEnsinoUser(Profile):
    nome = models.CharField(max_length=80)

    def __str__(self):
        return self.nome


class Distrito(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Endereco(models.Model):
    cep = models.CharField('CEP', max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=120, blank=True, null=True, help_text='Rua, beco, travessa')
    complemento = models.CharField(max_length=120, blank=True, null=True)
    bairro = models.CharField(max_length=120, blank=True, null=True)
    cidade = models.CharField(max_length=120, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    uf = models.CharField('UF', max_length=2, blank=True, null=True)

    def __str__(self):
        if self.logradouro is None:
            return ''
        return self.logradouro


class Escola(models.Model):
    """Represents a Escola model."""

    nome = models.CharField(max_length=100)
    referencia_escola = models.IntegerField(default=None, blank=True, null=True)
    codigo_inep = models.CharField(max_length=8, blank=True, null=True)
    gestor = models.ForeignKey(Gestor, default=None, blank=True, null=True)
    distrito = models.ForeignKey(Distrito, default=None, blank=True, null=True)
    slug = models.SlugField(
        default=None, blank=True, null=True, unique=True, max_length=500)
    endereco = models.OneToOneField(
        Endereco, on_delete=models.CASCADE, blank=True, null=True)
    imagem = models.ImageField(
        upload_to='escolas/%Y/%m/%d/', blank=True, null=True)

    primeiro_bimestre_ativo = models.BooleanField(default=True)
    segundo_bimestre_ativo = models.BooleanField(default=False)
    terceiro_bimestre_ativo = models.BooleanField(default=False)
    quarto_bimestre_ativo = models.BooleanField(default=False)

    objects = EscolaQuerySet.as_manager()

    tags = models.ManyToManyField("app.Tag", blank=True)

    def save(self, *args, **kwargs):
        """Sobrescreve o comportamento do padrão para gerar o slug."""
        if self.slug is None:
            self.slug = slugify(self.nome)
        super(Escola, self).save(*args, **kwargs)

    @classmethod
    def create(cls, nome):
        """Create a new school instance."""
        escola = cls(nome=nome)
        escola.save()
        return escola

    def get_alunos_count(self):
        """Retorna o número de alunos da escola."""
        alunos = Aluno.objects.filter(escola=self)
        return alunos.count()

    def __str__(self):
        return self.nome


class Tag(models.Model):
    name = models.CharField(max_length=30)


class Professor(Profile):
    """Entidade professor."""

    nome = models.CharField(max_length=80)
    escola = models.ManyToManyField(Escola, blank=True)
    matricula = models.CharField(default='', max_length=30)
    funcao = models.CharField(default='', max_length=150)

    # Novo relacionamento do professor com as turmas.
    classes = models.ManyToManyField(
        'Turma', through='TurmaDisciplina', related_name='turmas')

    objects = ProfessorQuerySet.as_manager()

    def turmas(self, escola, status=1):
        """Retorna turmas ativas do professor.

        Seleciona as turmas ativas que o professor leciona em uma escola
        específica.

        TODO: Substituir o número mágico '1' do parâmetro status. Corresponde a
        constante Turma.ATIVA, mas dá erro de compilação ao tentar passa-la
        como valor nesse ponto.
        """
        return self.turma_set.filter(status=status, escola=escola)

    def get_disciplinas_ids(self, escola):
        """Retorna a lista de disciplinas, sem repetições."""
        return TurmaDisciplina.objects.filter(
            professor=self,
            turma__escola=escola).values_list(
            'disciplina', flat=True).distinct()

    def get_escolas_json(self):
        """Retorna um dictionay de escolas associadas ao perfil."""
        data = []
        for esc in self.escola.all():
            image_url = ''
            if esc.imagem:
                image_url = esc.imagem.url

            esc_dict = {
                'id': esc.id,
                'nome': esc.nome,
                'slug': esc.slug,
                'imagem': image_url,
                'quantidadeAlunos': esc.get_alunos_count()
            }

            data.append(esc_dict)
        return data

    def __str__(self):
        return self.nome


class TurmaDisciplina(models.Model):
    professor = models.ForeignKey(Professor, related_name='grade_curricular')
    turma = models.ForeignKey('Turma', related_name='vinculo')
    disciplina = models.ForeignKey('Disciplina')

    def __str__(self):
        return "{0}-{1}".format(self.turma, self.disciplina)


class Responsavel(Profile):
    nome = models.CharField(max_length=80)
    escola = models.ForeignKey(Escola, default=None, blank=True, null=True)
    cpf = models.CharField(max_length=11, blank=True, null=True)
    telefone = models.CharField(max_length=16, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)

    objects = ResponsavelQuerySet.as_manager()

    class Meta:
        ordering = ['id']

    def get_username(self):
        if self.user is not None:
            return self.user.username
        else:
            return 'Usuário não definido'

    def __str__(self):
        return self.nome


class Disciplina(models.Model):
    nome = models.CharField(max_length=60)
    is_prova_brasil = models.BooleanField(
        default=False, verbose_name='Prova Brasil')

    objects = DisciplinaQuerySet.as_manager()

    @classmethod
    def create(cls, nome, is_prova_brasil=False):
        disciplina = cls(nome=nome, is_prova_brasil=is_prova_brasil)
        disciplina.save()
        return disciplina

    def __str__(self):
        if not self.is_prova_brasil:
            return self.nome
        else:
            return self.nome + ' (Prova Brasil)'


class Descritor(models.Model):
    cod = models.CharField(max_length=5)
    descricao = models.CharField(max_length=255)
    disciplina = models.ForeignKey(
        Disciplina, default=None, blank=True, null=True)
    serie = models.IntegerField(
        choices=SERIES_CHOICES, default=series_enum.ano_5_fundamental)

    def __str__(self):
        return "[{0}][{1}o. Ano] {2}-{3}".format(
            self.disciplina, self.serie, self.cod, self.descricao)


class Aula(models.Model):
    disciplina = models.ForeignKey(Disciplina)
    assunto = models.CharField(max_length=255)
    bimestre = models.IntegerField(choices=BIMESTRE_CHOICES)
    serie = models.IntegerField(choices=SERIES_CHOICES)
    ordem = models.IntegerField(default=0)

    @classmethod
    def create(cls, disciplina, assunto, serie, bimestre):
        aula = cls(
            disciplina=disciplina,
            assunto=assunto, serie=serie, bimestre=bimestre)
        aula.save()
        return aula

    def __str__(self):
        return self.assunto

    class Meta:
        ordering = ['assunto', 'ordem']


class VimeoThumbnailCache(models.Model):
    uri = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uri


class Attachment(models.Model):
    aula = models.ForeignKey(Aula, related_name='attachments')
    uri = models.URLField()
    thumbnail = models.OneToOneField(
        VimeoThumbnailCache, blank=True, null=True, on_delete=models.SET_NULL)
    titulo = models.CharField(
        max_length=30, default="", blank=True, null=True)
    descricao = models.CharField(
        max_length=190, default="", blank=True, null=True)
    attach_type = models.IntegerField(
        choices=ATTACH_TYPE_CHOICE, default=attach_type_enum.youtube_link)

    objects = AttachmentQuerySet.as_manager()

    @classmethod
    def create(cls, aula, uri, descricao):
        attach = cls(
            aula=aula, uri=uri, descricao=descricao)
        attach.save()
        return attach

    def __str__(self):
        return self.aula.assunto


def _gera_token_aluno():
    token = ''

    for i in range(8):
        rand_digit = str(randint(0, 9))
        token += rand_digit

    if not Aluno.objects.filter(token=token):
        return token

    _gera_token_aluno()


class Aluno(Profile):
    nome = models.CharField(max_length=80)
    nome_social = models.CharField(max_length=80, blank=True, null=True)
    responsaveis = models.ManyToManyField(Responsavel, blank=True)
    serie_atual = models.IntegerField(choices=SERIES_CHOICES, default=5)
    data_nascimento = models.date = models.DateField(
        default=None, blank=True, null=True)
    matricula = models.CharField(max_length=30, unique=False)
    escola = models.ForeignKey(Escola, default=None, blank=True, null=True)
    token = models.CharField(max_length=8, blank=True, null=True)
    codigo_inep = models.CharField(max_length=12, blank=True, null=True)

    objects = AlunoQuerySet.as_manager()

    def get_channels(self):
        """Retorna um array de channel for push notifications."""
        channels = []
        for r in self.responsaveis.all():
            channels.append('Responsavel_{0}'.format(r.id))

        return channels

    def turmas(self, status):
        """Retorna todas as turmas ao qual o aluno está matriculado"""
        return self.turma_set.filter(status=status)

    def turma_atual_id(self):
        """Esse método assume que um aluno pode pertencer apenas uma turma
        em qualquer tempo. Esse comportamento é comum para controle de escolas
        de ensino fundamental brasileiras."""

        turma = self.turma_set.first()
        if turma is not None:
            return turma.identificador

        return ""

    def turma_atual(self):
        return self.turma_set.first()

    def ttl_exercicios_log(self):
        return ExercicioLog.objects.filter(aluno=self).count()

    def ttl_respostas(self):
        return Resposta.objects.filter(aluno=self).count()

    def ttl_videos(self):
        return HistoricoAulasAssistidas.objects.filter(aluno=self).count()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk is None:
            self.token = _gera_token_aluno()

        super().save()

    def __str__(self):
        return self.nome


def setup_user_role(sender, instance, **kwargs):
    if instance.__class__.__name__ == "Administrador":
        instance.role = Profile.ADMINISTRATOR
    elif instance.__class__.__name__ == "Gestor":
        instance.role = Profile.GESTOR_ESCOLAR
    elif instance.__class__.__name__ == "Aluno":
        instance.role = Profile.STUDENT
    elif instance.__class__.__name__ == "Responsavel":
        instance.role = Profile.RESPOSIBLE
    elif instance.__class__.__name__ == "Professor":
        instance.role = Profile.PROFESSOR


def save_gestor_role(sender, instance, **kwargs):
    instance.role = Profile.GESTOR_ESCOLAR


def save_student_role(sender, instance, **kwargs):
    instance.role = Profile.STUDENT


def save_reponsible_role(sender, instance, **kwargs):
    instance.role = Profile.RESPOSIBLE


def save_professor_role(sender, instance, **kwargs):
    instance.role = Profile.PROFESSOR


pre_save.connect(save_gestor_role, sender=Gestor)
pre_save.connect(save_student_role, sender=Aluno)
pre_save.connect(save_reponsible_role, sender=Responsavel)
pre_save.connect(save_professor_role, sender=Professor)
pre_save.connect(setup_user_role, sender=Administrador)


class HistoricoAulasAssistidas(models.Model):
    aula = models.ForeignKey(Aula)
    """O attachement é de fato a aula que o aluno assistiu

    É uma próxima versão do sistema podemos corrigir a questão semântica
    envolvendo o nome dessa classe que deveria se chamar aula.

    Nota: o relacionamento está sendo criado como nullable para minimizar o
    impacto no banco de dados.
    """
    attachment = models.ForeignKey(
        Attachment, default="", blank=True, null=True)
    aluno = models.ForeignKey(Aluno)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = HistoricoAulasAssistidasQuerySet.as_manager()

    @classmethod
    def create(cls, aula, aluno):
        hist = cls(aula=aula, aluno=aluno)
        hist.save()
        return hist

    @classmethod
    def register_viewing(cls, aula, attachment, aluno):
        hist = cls(aula=aula, aluno=aluno, attachment=attachment)
        hist.save()
        return hist


class Turma(models.Model):
    """ Classe que representa o modelo de uma turma """

    # Possíveis status de uma turma
    NOVA = 0
    ATIVA = 1
    ARQUIVADA = 2

    TURMA_STATUS_CHOICES = (
        (NOVA, 'Nova'),
        (ATIVA, 'Ativa'),
        (ARQUIVADA, 'Arquivada'),
    )

    identificador = models.CharField(max_length=40)
    descricao = models.CharField(max_length=200)
    letra = models.CharField(max_length=5, default='')
    escola = models.ForeignKey(Escola)
    alunos = models.ManyToManyField(Aluno, blank=True)
    serie = models.IntegerField(
        choices=SERIES_CHOICES, default=series_enum.ano_5_fundamental)
    professores = models.ManyToManyField(Professor, blank=True)
    status = models.IntegerField(choices=TURMA_STATUS_CHOICES, default=NOVA)
    turno = models.CharField(max_length=15, choices=TURNO_CHOICE, default=turno_enum.matutino)

    objects = TurmaQuerySet.as_manager()

    def set_status(self, status):
        self.status = status

    def display_name(self):
        """Composição do Ano, Letra e Turno da Turma"""
        return "{0}&deg; {1} {2}.".format(self.serie, self.letra, self.turno)

    @classmethod
    def create(
            cls,
            escola,
            identificador, descricao, serie=series_enum.ano_5_fundamental):
        turma = cls(
            escola=escola,
            identificador=identificador, descricao=descricao, serie=serie)
        turma.save()
        return turma

    def alunos_count(self):
        return self.alunos.count()

    def __str__(self):
        return '{0} - {1} - {3} - {2}'.format(self.escola.nome, self.serie, self.turno, self.letra)


class Exercicio(models.Model):
    descritor = models.ForeignKey(Descritor, blank=True, null=True)
    aula = models.ForeignKey(Aula, related_name='exercicios')
    enunciado = models.TextField()
    complemento = models.TextField(default=None, blank=True, null=True)
    imagem = models.ImageField(
        upload_to='res/%Y/%m/%d/', blank=True, null=True)
    classificacao = models.IntegerField(
        choices=CLASSIFICACAO_CHOICES, default=None, blank=True, null=True)

    objects = ExercicioQuerySet.as_manager()

    def get_alternativa(self, index):
        """Retorna alternativa da questão conforme index."""

        qs = Alternativa.objects.filter(exercicio=self)
        return qs[index]

    def get_enunciado_stripped(self):
        doc = html.fromstring(self.enunciado)
        return doc.text_content()

    get_enunciado_stripped.short_description = "Enunciado"

    def alternativa_correta(self):
        qs = Alternativa.objects.filter(exercicio=self, correta=True)
        return qs[0]

    @classmethod
    def create(cls, aula, enunciado, complemento=''):
        exercicio = cls(
            aula=aula, enunciado=enunciado, complemento=complemento)
        exercicio.save()
        return exercicio

    def disciplina(self):
        return self.aula.disciplina

    def prova_brasil(self):
        return self.aula.disciplina.is_prova_brasil

    def resposta(self):
        return 9

    def __str__(self):
        return self.enunciado

    class Meta:
        ordering = ['aula__assunto']


class ExercicioLog(models.Model):
    exercicio = models.ForeignKey(Exercicio)
    aluno = models.ForeignKey(Aluno)
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, aluno, exercicio):
        logex = cls(exercicio=exercicio, aluno=aluno)
        logex.save()
        return logex


class Alternativa(models.Model):
    exercicio = models.ForeignKey(Exercicio, related_name='alternativas')
    enunciado = models.TextField()
    correta = models.BooleanField(default=False)
    explicacao = models.TextField(default=None, blank=True, null=True)
    imagem = models.ImageField(
        verbose_name='Imagem Alternativa',
        upload_to='alt/%Y/%m/%d/', blank=True, null=True)
    img_resposta = models.ImageField(
        verbose_name='Imagem Resposta',
        upload_to='resp/%Y/%m/%d/', blank=True, null=True)

    @classmethod
    def create(cls, exercicio, enunciado, explicacao, correta=False):
        alternativa = cls(
            exercicio=exercicio,
            enunciado=enunciado, explicacao=explicacao, correta=correta)
        alternativa.save()
        return alternativa

    def exercicio_truncado(self):
        return '{:.150}'.format(self.exercicio.enunciado)

    def __str__(self):
        return self.enunciado

    class Meta:
        ordering = ['id']


class Resposta(models.Model):
    aluno = models.ForeignKey(Aluno)
    exercicio = models.ForeignKey(Exercicio)
    alternativa = models.ForeignKey(Alternativa)
    date = models.DateField(auto_now_add=True)  # Usado para filtros
    timestamp = models.DateTimeField(auto_now_add=True)  # Usado para retorno de data e hora

    objects = RespostaQuerySet.as_manager()

    @classmethod
    def post_response(cls, aluno_id, exercicio_id, alternativa_id):
        aluno = Aluno.objects.get(pk=aluno_id)
        exercicio = Exercicio.objects.get(pk=exercicio_id)
        alternativa = Alternativa.objects.get(pk=alternativa_id)

        return cls.aplicar_resposta(aluno, exercicio, alternativa)

    @classmethod
    def aplicar_resposta(cls, aluno, exercicio, alternativa):
        # Verifica se a alternativa selecionada pertence ao exercício
        if exercicio.id != alternativa.exercicio.id:
            raise ValueError('Alternativa Inválida.')

        # Verifica se já existe uma resposta do aluno para o exercício
        query = Resposta.objects.filter(aluno=aluno, exercicio=exercicio)

        if query.count() == 0:
            resposta = cls(
                aluno=aluno, exercicio=exercicio, alternativa=alternativa)
            date = datetime.today()
            resposta.date = date
            resposta.save()
        else:
            resposta = query[0]

        # for r in Resposta.objects.all():
        #     print('{0} {1}'.format(aluno.id, exercicio.id))
        # print('----------------------------------------------')
        # FIX: o app deve guardar apenas a primeria resposta do aluno para o
        # exercicio.
        # else:
        #    resposta = query[0]
        #    resposta.alternativa = alternativa

        return resposta

    @classmethod
    def get_resposta(cls, aluno_id, exercicio_id):
        queryset = Resposta.objects.filter(
            aluno__id=aluno_id, exercicio__id=exercicio_id)

        if queryset.count() != 0:
            return queryset[0].alternativa.id
        else:
            return 0

    def resultado(self):
        if self.exercicio.alternativa_correta() == self.alternativa:
            return 1

        return 0

    def __str__(self):
        return '{0}, {1}, {2}, {3}'.format(
            self.aluno,
            self.exercicio, self.alternativa, self.alternativa.correta)


class IndicadorDesempenho(object):
    def __init__(self, serie, resultado):
        self.serie = serie
        self.resultado = resultado


class DesempenhoGeral(object):
    def __init__(self, provabrasil, reforco):
        self.provabrasil = provabrasil
        self.reforco = reforco


class AproveitamentoDisciplina(object):
    def __init__(self, disciplina_id, nome, aproveitamento):
        self.id = disciplina_id
        self.nome = nome
        self.aproveitamento = aproveitamento


class Desempenho(object):
    def __init__(self, aulas_assistidas, disciplinas, visualizacoes_unicas):
        self.aulas_assistidas = aulas_assistidas
        self.visualizacoes_unicas = visualizacoes_unicas
        self.disciplinas = disciplinas


class TurmaStates(object):
    def __init__(self, id, identificador, aproveitamento):
        self.id = id
        self.identificador = identificador
        self.aproveitamento = aproveitamento


class SerieStates(object):
    def __init__(
            self, serie, total_alunos, desempenho, turmas):
        self.serie = serie
        self.total_alunos = total_alunos
        self.desempenho = desempenho
        self.turmas = turmas


class DesempenhoGeralTurmaDTO(object):
    def __init__(
            self, turma, total_alunos,
            prova_brasil, super_reforco):
        self.turma = turma
        self.total_alunos = total_alunos
        self.prova_brasil = prova_brasil
        self.super_reforco = super_reforco


class AproveitaMentoAnaliticoDTO(object):
    def __init__(self, id, nome, acertos, erros, descritores=None):
        self.id = id
        self.nome = nome
        self.acertos = acertos
        self.erros = erros
        self.descritores = descritores


class DesempenhoDisciplinaAlunoDTO(object):
    def __init__(self, disciplina_id, nome, erros, acertos, aproveitamento, descritores=None, assuntos=None):
        self.disciplina_id = disciplina_id
        self.nome = nome
        self.erros = erros
        self.acertos = acertos
        self.aproveitamento = aproveitamento
        self.descritores = descritores
        self.assuntos = assuntos


class AproveitamentoWrapperDTO(object):
    def __init__(self, id, disciplinas):
        self.id = id
        self.disciplinas = disciplinas


class DescritorDTO(object):
    def __init__(self, id, nome, descricao, acertos, erros):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.acertos = acertos
        self.erros = erros


class AssuntoDTO(object):
    def __init__(self, id, assunto, ordem, acertos, erros):
        self.id = id
        self.assunto = assunto
        self.ordem = ordem
        self.acertos = acertos
        self.erros = erros


class UserSchoolRelationshipManager (models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE)

    @classmethod
    def associate_by_school_tag(cls, user, tag):
        """
        Associa todas as escolas registradas a tag informada ao user
        :param user:
        :param tag:
        :return:
        """
        escolas = Escola.objects.filter(tags=tag)
        for e in escolas:
            UserSchoolRelationshipManager.objects.create(
                user=user, escola=e)

    @classmethod
    def associate_by_district(cls, user, district):
        escolas = Escola.objects.filter(distrito=district)
        for e in escolas:
            UserSchoolRelationshipManager.objects.create(
                user=user, escola=e)