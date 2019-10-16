import time

from celery import shared_task
from .csv_to_database import importa_dados_base
from .gerar_carta_credenciais import gerar_carta

import logging

logger = logging.getLogger(__name__)


@shared_task
def import_data(arquivo):
    logger.info('--> import_data')
    importa_dados_base(arquivo)
    logger.info('<-- import_data')


@shared_task
def gerar_carta_task(user_email, queryset):
    logger.info('--> gerar_carta')
    gerar_carta(user_email, queryset)
    logger.info('<-- gerar_carta')


@shared_task
def slow_task():
    logger.info('Started task, processing...')
    time.sleep(5)
    logger.info('Finished Task')
    return True
