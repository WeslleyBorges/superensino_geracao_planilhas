from app import views
from django.conf.urls import url


urlpatterns = [
    url(r'^home/$', views.home, name='home'),
    url(r'^importar_dados_formulario/$', views.upload_file, name='upload_file'),
    url(r'^testtask/$', views.task_debug, name='testtask'),
    url(r'^papaya/$', views.papaya, name='testtask'),
]
