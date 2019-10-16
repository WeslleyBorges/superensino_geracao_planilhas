from django.contrib import admin
import csv
from django.http import HttpResponse
from data.wharehouse.models import ExercisesDataWharehouse


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        # field_names = [field.name for field in meta.fields]
        field_names = [
            'escola',
            'turma',
            'serie',
            'bimestre',
            'aluno_id',
            'exercicio_id',
            'disciplina',
            'is_prova_brasil',
            'resposta_id',
            'gabarito_id',
        ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


@admin.register(ExercisesDataWharehouse)
class ExercisesDataWharehouseAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        'escola',
        'turma',
        'serie',
        'bimestre',
        'aluno_id',
        'exercicio_id',
        'disciplina',
        'is_prova_brasil',
        'resposta_id',
        'gabarito_id',
    )
    list_filter = (
        'escola',
        'turma',
        'serie',
        'bimestre',
        'disciplina',
        'aluno',
        'is_prova_brasil',
    )
    actions = ["export_as_csv"]
