from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from app.models import Exercicio
from ajax_select.fields import AutoCompleteSelectField
from django import forms

class UserAdminCreationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']


class ExercicioForm(ModelForm):
    class Meta:
        model = Exercicio
        fields = ['aula', 'descritor', 'classificacao']

    aula = AutoCompleteSelectField('aulas')

    def __init__(self, *args, **kwargs):
        super(ExercicioForm, self).__init__(*args, **kwargs)
        self.fields['aula'].widget.attrs['style'] = 'width:600px;'

class UploadFileForm(forms.Form):
    file = forms.FileField()