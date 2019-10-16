from ajax_select import register, LookupChannel
from .models import Aula


@register('aulas')
class AulasLookup(LookupChannel):

    model = Aula

    def get_query(self, q, request):
        return self.model.objects.filter(
            assunto__unaccent__icontains=q).order_by('id')[:50]

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item.assunto
