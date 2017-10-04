# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-31 18:29
from __future__ import unicode_literals

from django.db import migrations
from django.template.defaultfilters import slugify


attr_to_keyword = dict(
    aquisition='Acquisition/Contracts',
    human_capital='Human Capital',
    cloud='Cloud',
    data_centers='Data Centers',
    cybersecurity='Cybersecurity',
    privacy='Privacy',
    shared_services='Shared Services',
    it_project_management='IT Project Management',
    software='Software',
    digital_services='Digital Services',
    mobile='Mobile',
    hardware='Hardware/Government Furnished Equipment (GFE)',
    transparency='IT Transparency (Open Data, FOIA, Public Records, etc.)',
    statistics='Agency Statistics',
    customer_services='Customer Services',
    governance='Governance',
    financial_systems='Financial Systems',
    budget='Budget',
    governance_org_structure='Governance - Org Structure',
    governance_implementation='Governance - Implementation',
    data_management='Data Management/Standards',
    definitions='Definitions',
    reporting='Reporting'
)
keyword_to_attr = {keyword:attr for attr, keyword in attr_to_keyword.items()}


# copy-pasted to ensure migrations are consistent over time
def priority_split(text, *splitters):
    """When we don't know which character is being used to combine text, run
    through a list of potential splitters and split on the first"""
    present = [s for s in splitters if s in text]
    # fall back to non-present splitter; ensures we have a splitter
    splitters = present + list(splitters)
    splitter = splitters[0]
    return [seg.strip() for seg in text.split(splitter) if seg.strip()]


def forward(apps, schema_editor):
    Keyword = apps.get_model('reqs', 'Keyword')
    KeywordConnect = apps.get_model('reqs', 'KeywordConnect')
    Requirement = apps.get_model('reqs', 'Requirement')
    keyword_cache, connections = {}, []
    for req in Requirement.objects.all():
        req_keywords = []
        for field_name, tag_name in attr_to_keyword.items():
            if getattr(req, field_name):
                req_keywords.append(tag_name)
        req_keywords.extend(priority_split(req.other_keywords, ';', ','))
        for keyword in req_keywords:
            kw_slug = slugify(keyword)
            if kw_slug not in keyword_cache:
                keyword_cache[kw_slug] = Keyword.objects.create(
                    name=keyword, slug=kw_slug)
            connections.append(KeywordConnect(
                tag=keyword_cache[kw_slug], content_object=req))
    KeywordConnect.objects.bulk_create(connections)


def backward(apps, schema_editor):
    Keyword = apps.get_model('reqs', 'Keyword')
    KeywordConnect = apps.get_model('reqs', 'KeywordConnect')
    connections = KeywordConnect.objects.prefetch_related('tag',
                                                          'content_object')
    for conn in connections:
        if conn.tag.name in keyword_to_attr:
            setattr(conn.content_object, keyword_to_attr[conn.tag.name], True)
        else:
            other_keywords = [
                kw.strip()
                for kw in conn.content_object.other_keywords.split(';')
                if kw.strip()
            ]
            other_keywords.append(conn.tag.name)
            conn.content_object.other_keywords = ';'.join(other_keywords)
        conn.content_object.save()
    KeywordConnect.objects.all().delete()
    Keyword.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [('reqs', '0012_auto_20170131_1827')]
    operations = [migrations.RunPython(forward, backward)]