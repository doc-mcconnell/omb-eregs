# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-02 00:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reqs', '0015_remove_policy_public'),
    ]

    operations = [
        migrations.RunSQL("""
            UPDATE reqs_policy
            SET workflow_phase='cleanup'
            WHERE workflow_phase='no_doc'
            AND id IN (SELECT policy_id from document_docnode)
        """)
    ]
