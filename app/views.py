from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import generic
from model_mommy import mommy

from app import models as domain
from app.models import Aluno, Gestor, Professor, Responsavel, Escola, SuperEnsinoUser, UserSchoolRelationshipManager
from app.tasks import slow_task
from .forms import UploadFileForm
from .tasks import import_data
from oauth2_provider.models import AccessToken

@login_required
def home(request, template_name='app/home.html'):
    return render(request, template_name)


def authenticate_user(request, template_name='app/login.html'):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            data = {
                'errors': 'Nome de usuário ou password incorretos'
            }
            return render(request, template_name, data)
    else:
        return render(request, template_name)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csvfile = request.FILES['file']
            arquivo_lido_string = csvfile.read().decode('utf-8')

            import_data.delay(arquivo_lido_string)

            return render(request, 'app/feedback_import_data.html')
    else:
        form = UploadFileForm()
    return render(request, 'app/import_data_form.html', {'form': form})


def task_debug(request):
    slow_task.delay()
    return HttpResponse('Ok')


def papaya(request):
    data = []

    seu_list = SuperEnsinoUser.objects.all()
    prof_list = Professor.objects.all()

    queryset_list = list(seu_list)[:-2] + list(prof_list)

    for gest_prof in queryset_list:
        nome = gest_prof.nome
        username = gest_prof.user.username
        relations = UserSchoolRelationshipManager.objects.filter(user=gest_prof.user)

        distrito = 'NÃO POSSUI'

        if gest_prof.role == 8:
            distrito = 'TODOS' if relations.count() >= 50 else relations[0].escola.distrito

        if gest_prof.role == 4:
            distrito = distrito if gest_prof.escola.count() == 0 else gest_prof.escola.all()[0].distrito.nome

        escola = 'NÃO POSSUI'

        if gest_prof.role != 8:
            escolas_count = gest_prof.escola.all().count()
            escola = gest_prof.escola.all()[0].nome if escolas_count > 0 else escola
        else:
            escola = 'TODAS DO DISTRITO'

        quantidade_acessos = AccessToken.objects.filter(user=gest_prof.user).count()
        cargo = 'PROFESSOR' if gest_prof.role != 8 else 'GESTOR'

        data.append((nome, username, cargo, distrito, escola, quantidade_acessos))

    file = open('estatisticas_gestores_professores.csv', 'w+')

    file.write('Nome,Login,Cargo,Distrito,Escola,Quantidade de acessos\n')

    for datum in data:
        file.write('%s,%s,%s,%s,%s,%s\n' % (datum[0], datum[1], datum[2], datum[3], datum[4], datum[5]))

    file.close()

    return HttpResponse({})