# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-07-22 16:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_auto_20180523_0229'),
    ]

    operations = [
        migrations.CreateModel(
            name='Administrador',
            fields=[
                ('profile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.Profile')),
                ('nome', models.CharField(max_length=80)),
            ],
            bases=('app.profile',),
        ),
    ]
