# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-12 00:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alternativa_img_resposta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alternativa',
            name='imagem',
            field=models.ImageField(blank=True, null=True, upload_to='alt/%Y/%m/%d/', verbose_name='Imagem Alternativa'),
        ),
        migrations.AlterField(
            model_name='alternativa',
            name='img_resposta',
            field=models.ImageField(blank=True, null=True, upload_to='resp/%Y/%m/%d/', verbose_name='Imagem Resposta'),
        ),
    ]
