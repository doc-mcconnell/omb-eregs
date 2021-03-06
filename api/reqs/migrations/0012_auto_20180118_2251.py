# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-18 22:51
from __future__ import unicode_literals

from django.db import migrations

def default_to_no_doc(apps, schema_editor):
    # From
    # https://docs.djangoproject.com/en/2.0/topics/migrations/#data-migrations
    #
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Policy = apps.get_model('reqs', 'Policy')
    Policy.objects.filter(workflow_phase='').update(workflow_phase='no_doc')

class Migration(migrations.Migration):

    dependencies = [
        ('reqs', '0011_auto_20180117_2323'),
    ]

    operations = [
        migrations.RunPython(default_to_no_doc)
    ]
