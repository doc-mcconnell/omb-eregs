# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-16 21:05
from __future__ import unicode_literals

from django.db import migrations


def forward(apps, schema_editor):
    Theme = apps.get_model('admin_interface', 'Theme')
    Theme.objects.filter(name='USWDS').update(
        css_header_background_color='#000000',
        css_header_link_hover_color='#edfcff',
        css_module_background_color='#222222',
        css_module_text_color='#cecfd1',
        css_module_link_color='#cecfd1',
        css_module_link_hover_color='#edfcff',
        css_generic_link_color='#112e51',
        css_generic_link_hover_color='#1067a6',
        css_save_button_background_color='#1067a6',
        css_save_button_background_hover_color='#112e51',
        name='OMB',
    )

def backwards(apps, schema_editor):
    Theme = apps.get_model('admin_interface', 'Theme')
    Theme.objects.filter(name='OMB').update(
        css_header_background_color='#112E51',
        css_header_link_hover_color='#E1F3F8',
        css_module_background_color='#205493',
        css_module_text_color='#FFFFFF',
        css_module_link_color='#FFFFFF',
        css_module_link_hover_color='#E1F3F8',
        css_generic_link_color='#205493',
        css_generic_link_hover_color='#0071BC',
        css_save_button_background_color='#205493',
        css_save_button_background_hover_color='#112E51',
        name='USWDS',
    )

class Migration(migrations.Migration):

    dependencies = [
        ('ereqs_admin', '0001_initial'),
    ]

    operations = [migrations.RunPython(forward, backwards)]
