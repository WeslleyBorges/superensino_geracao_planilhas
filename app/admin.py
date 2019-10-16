from django.contrib import admin
from app import models
from django_summernote.admin import SummernoteModelAdmin
from django import forms
from django_summernote.widgets import SummernoteWidget
from django.utils.translation import gettext_lazy as _
from app.forms import ExercicioForm
from data.wharehouse.models import ExercisesDataWharehouse
from .tasks import gerar_carta_task
import json
from django.core import serializers

admin.site.site_header = 'Super Ensino Admin'


class IncorrectHtmlFilter(admin.SimpleListFilter):
    title = _('tags incorretas')
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        return (
            ('codinvalido', _('cod. inválido')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'codinvalido':
            return queryset.filter(explicacao__regex=r'&ensp|&emsp(?!;)')


@admin.register(models.Distrito)
class DistritoAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SuperEnsinoUser)
class SuperEnsinoUserAdmin(admin.ModelAdmin):
    pass

@admin.register(models.UserSchoolRelationshipManager)
class UserSchoolRelationshipManagerAdmin(admin.ModelAdmin):
    pass

@admin.register(models.TurmaDisciplina)
class TurmaDisciplinaAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Endereco)
class GestorAdmin(admin.ModelAdmin):
    list_display = ('id', 'logradouro')


@admin.register(models.Escola)
class EscolaAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Professor)
class ProfessorAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'genero', 'role', 'get_username')


def remove_aluno_history(modeladmin, request, queryset):
    """
    Exclui todos os dados de exercícios realizados e aulas visualizadas dos alunos.

    :param modeladmin:
    :param request:
    :param queryset:
    :return:
    """
    #for aluno in queryset:
    models.ExercicioLog.objects.filter(aluno__in=queryset).delete()
    models.Resposta.objects.filter(aluno__in=queryset).delete()
    models.HistoricoAulasAssistidas.objects.filter(aluno__in=queryset).delete()
    ExercisesDataWharehouse.objects.filter(aluno__in=queryset).delete()


remove_aluno_history.short_description = "Excluir histórico dos alunos selecionados"


def serialize_aluno(aluno):
    username_resp1 = '-'
    username_resp2 = '-'

    try:
        username_resp1 = aluno.responsaveis.all()[0].user.username
    except IndexError:
        pass

    if username_resp1 != '-':
        try:
            username_resp2 = aluno.responsaveis.all()[1].user.username
        except IndexError:
            pass

    turma_aluno = aluno.turma_atual()

    obj = {
        'id': aluno.pk,
        'nome': aluno.nome,
        'matricula': aluno.matricula,
        'responsaveis': [
            {'username': username_resp1},
            {'username': username_resp2}
        ],
        'escola_nome': aluno.escola.nome,
        'escola_slug': aluno.escola.slug,
        'aluno_username': aluno.user.username,
        'serie': aluno.serie_atual,
        'turma_letra': turma_aluno.letra,
        'turno': 'MAT' if turma_aluno.turno.startswith('M') else 'VESP'
    }

    return obj


def gerar_carta_credenciais(modeladmin, request, queryset):
    user_email = request.user.email

    aluno_list = []

    for qs in queryset:
        aluno_list.append(qs)

    serialized_queryset = []

    for aluno in aluno_list:
        serialized_queryset.append(serialize_aluno(aluno))

    gerar_carta_task.delay(user_email, serialized_queryset)


gerar_carta_credenciais.short_description = "Gerar carta com as credenciais em PDF"


@admin.register(models.Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'genero', 'get_username', 'ttl_exercicios_log', 'ttl_respostas', 'ttl_videos')
    list_filter = ('escola', 'serie_atual',)
    actions = [remove_aluno_history, gerar_carta_credenciais]
    readonly_fields = ['token']


@admin.register(models.Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'descricao', 'escola', 'serie')
    list_filter = ('escola', 'serie',)


@admin.register(models.Descritor)
class Descritor(admin.ModelAdmin):
    list_display = ('cod', 'descricao', 'disciplina', 'serie')
    list_filter = ('disciplina',)


@admin.register(models.Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'is_prova_brasil')
    list_filter = ('is_prova_brasil',)


class AttachmentInline(admin.TabularInline):
    model = models.Attachment
    exclude = ['thumbnail', 'attach_type']
    extra = 1


@admin.register(models.Aula)
class AulaAdmin(admin.ModelAdmin):
    inlines = [AttachmentInline]
    list_display = ('ordem', 'disciplina', 'assunto', 'bimestre', 'serie')
    list_filter = ('disciplina', 'bimestre', 'serie')
    ordering = ('ordem', 'assunto', )


class AlternativaForm(forms.ModelForm):
    class Meta:
        widgets = {
            'enunciado': SummernoteWidget(),
            'explicacao': SummernoteWidget(),
        }


class AlternativaInline(admin.TabularInline):
    form = AlternativaForm
    model = models.Alternativa
    readonly_fields = ('id',)
    extra = 4
    min_num = 1
    max_num = 4


@admin.register(models.Exercicio)
class ExercicioAdmin(SummernoteModelAdmin):
    form = ExercicioForm
    # summer_note_fields = ('enunciado',)
    fieldsets = [
        (None, {'fields': ['aula', 'descritor', 'classificacao', 'imagem']}),
        ('Enunciado e Complemento',
            {'fields': ['enunciado', 'complemento']}),
    ]

    inlines = [
        AlternativaInline,
    ]
    list_display = (
        'id', 'aula', 'get_enunciado_stripped', 'disciplina', 'prova_brasil')
    ordering = ('aula', 'id',)
    list_filter = (
        'aula__disciplina__is_prova_brasil',
        'aula__bimestre', 'aula__serie', 'aula__disciplina', 'aula__assunto')
    search_fields = ['id', 'enunciado']


@admin.register(models.Alternativa)
class AlternativaAdmin(SummernoteModelAdmin):
    list_display = ('enunciado', 'exercicio_truncado', 'correta')
    search_fields = ['exercicio__enunciado']
    list_filter = (IncorrectHtmlFilter,)


@admin.register(models.Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'exercicio', 'alternativa')
    list_filter = ('aluno',)


@admin.register(models.ExercicioLog)
class ExercicioLogAdmin(admin.ModelAdmin):
    search_fields = ['aluno']
    list_display = ('aluno', 'exercicio', 'timestamp')
    list_filter = ('aluno', 'exercicio__aula__disciplina__is_prova_brasil')


@admin.register(models.HistoricoAulasAssistidas)
class HistoricoAulasAssistidasAdmin(admin.ModelAdmin):
    list_display = ('aula', 'aluno', 'timestamp')
    list_filter = ('aluno',)


@admin.register(models.Gestor)
class GestorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'genero', 'role', 'get_username')
