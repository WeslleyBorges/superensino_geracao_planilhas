# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-09-26 16:06
from __future__ import unicode_literals

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0058_auto_20190829_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='imagem',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, default='static/img/default_avatar_male.jpg', null=True, upload_to='profile/%Y/%m/%d/'),
        ),
    ]
