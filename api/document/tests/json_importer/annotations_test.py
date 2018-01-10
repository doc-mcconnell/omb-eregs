from document.json_importer.annotations import derive_annotations
from document.json_importer.importer import convert_node
from document.models import ExternalLink, FootnoteCitation

from .importer_test import PARA_WITH_LINK, text


def test_derive_annotations_works_with_nested_content():
    para = convert_node({
        "node_type": 'para',
        "content": [{
            "content_type": 'external_link',
            "href": 'http://one.org',
            "inlines": [
                text('foo'),
                {
                    "content_type": 'external_link',
                    "href": 'http://two.org',
                    "inlines": [text('bar')],
                },
                text('baz'),
                {
                    "content_type": 'external_link',
                    "href": 'http://three.org',
                    "inlines": [text('quux')],
                }
            ],
        }],
        "children": [],
    })
    annos = derive_annotations(para)

    assert len(annos) == 1

    links = annos[ExternalLink]
    assert len(links) == 3

    one = links[0]
    assert para.text[one.start:one.end] == 'foobarbazquux'

    two = links[1]
    assert para.text[two.start:two.end] == 'bar'

    three = links[2]
    assert para.text[three.start:three.end] == 'quux'


def test_derive_annotations_works_with_external_link():
    annos = derive_annotations(convert_node(PARA_WITH_LINK))

    assert len(annos) == 1
    assert len(annos[ExternalLink]) == 1
    link = annos[ExternalLink][0]
    assert link.href == 'http://example.org/'
    assert link.start == len('Hello ')
    assert link.end == link.start + len('there')


def test_derive_annotations_works_with_footnote_citation():
    para = convert_node({
        "node_type": 'para',
        "content": [{
            "content_type": 'footnote_citation',
            "inlines": [text('3')],
        }],
        "children": [{
            "node_type": "footnote",
            "marker": '3',
            "type_emblem": '3',
            "children": [],
            "content": [text('Hi I am a footnote')],
        }],
    })
    annos = derive_annotations(para)

    assert len(annos) == 1
    assert len(annos[FootnoteCitation]) == 1
    cit = annos[FootnoteCitation][0]
    assert cit.start == 0
    assert cit.end == 1
    assert cit.footnote_node.text == 'Hi I am a footnote'
