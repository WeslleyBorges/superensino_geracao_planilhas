# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-08-29 19:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0057_auto_20190826_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='imagem',
            field=models.ImageField(blank=True, default='static/img/default_avatar_male.jpg', null=True, upload_to='profile/%Y/%m/%d/'),
        ),
    ]
