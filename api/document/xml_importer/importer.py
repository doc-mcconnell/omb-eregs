import logging

from lxml import etree

from document.models import DocNode
from document.tree import XMLAwareCursor
from document.xml_importer.annotations import derive_annotations
from document.xml_importer.preprocess import (clean_content,
                                              standardize_content,
                                              warn_about_mismatches)
from reqs.models import Policy

logger = logging.getLogger(__name__)


def import_xml_doc(policy: Policy, xml: etree.ElementBase,
                   ignore_preamble=False) -> XMLAwareCursor:
    DocNode.objects.filter(policy=policy).delete()
    if not ignore_preamble:
        warn_about_mismatches(policy, xml)
    standardize_content(xml)
    clean_content(xml)

    root = convert_to_tree(xml, policy=policy)
    root.nested_set_renumber()
    logger.info('Created %s nodes for %s', root.subtree_size(),
                policy.title_with_number)
    annotations_by_cls = derive_annotations(root)
    for cls, annotations in annotations_by_cls.items():
        cls.objects.bulk_create(annotations)
        logger.info('Created %s %s', len(annotations),
                    cls._meta.verbose_name_plural)
    return root


def truncate_char_field(xml_node: etree.ElementBase, field_name: str) -> str:
    value = xml_node.attrib.get(field_name, '')
    field = DocNode._meta.get_field(field_name)
    if len(value) > field.max_length:
        logger.warn(f'Truncating "{value}" to {field.max_length} characters')
        value = value[:field.max_length]
    return value


def convert_to_tree(xml_node: etree.ElementBase, parent=None,
                    **kwargs) -> XMLAwareCursor:
    cursor_args = {
        'node_type': xml_node.tag,
        'marker': truncate_char_field(xml_node, 'marker'),
        'text': content_text(xml_node),
        'title': truncate_char_field(xml_node, 'title'),
        **kwargs,
    }
    if 'emblem' in xml_node.attrib:
        cursor_args['type_emblem'] = xml_node.attrib['emblem']
    if parent:
        cursor = parent.add_child(**cursor_args)
    else:
        cursor = XMLAwareCursor.new_tree(**cursor_args)
    cursor.xml_node = xml_node

    for xml_child in xml_node.xpath('./*[not(self::content)]'):
        convert_to_tree(xml_child, cursor, **kwargs)

    return cursor


def content_text(xml_node: etree.ElementBase):
    """Fetch just the text from a node. We'll assume it's been preprocessed to
    have a single <content/> child."""
    content_node = xml_node.find('./content')
    if content_node is None:
        return ''
    else:
        return ''.join(content_node.itertext())
