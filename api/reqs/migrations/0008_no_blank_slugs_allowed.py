# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-02 20:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reqs', '0007_populate_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policy',
            name='slug',
            field=models.SlugField(max_length=1024),
        ),
    ]