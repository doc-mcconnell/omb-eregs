import pytest
from model_mommy import mommy

from document.serializers import meta
from document.serializers.doc_cursor import DocCursorSerializer
from document.tree import DocCursor
from reqs.models import Policy


@pytest.mark.parametrize('node_type', ('para', 'table', 'something-else'))
@pytest.mark.parametrize('is_root', (True, False))
@pytest.mark.django_db
def test_descendant_footnotes_meta(node_type, is_root):
    """Only the root and "table" nodes should get descendant_footnotes."""
    policy = mommy.make(Policy)
    cursor = DocCursor.new_tree(node_type, policy=policy)
    cursor.nested_set_renumber()
    meta_obj = meta.Meta(cursor, is_root, policy)
    result = meta.MetaSerializer(
        meta_obj,
        context={'parent_serializer': DocCursorSerializer()},
    ).data
    if node_type == 'table' or is_root:
        assert 'descendant_footnotes' in result
    else:
        assert 'descendant_footnotes' not in result


@pytest.mark.django_db
def test_descendant_footnotes():
    """We pull out footnotes of all descendants, and only descendants."""
    policy = mommy.make(Policy)
    root = DocCursor.new_tree('root', policy=policy)
    ftnt_a = root.add_child('footnote', 'a')
    root.add_child('para')
    ftnt_b = root['para_1'].add_child('footnote', 'b')
    root.add_child('list')
    root['list_1'].add_child('para')
    root['list_1'].add_child('para')
    root['list_1'].add_child('para')
    ftnt_c = root['list_1']['para_3'].add_child('footnote', 'c')
    root.nested_set_renumber()

    root['para_1'].footnotecitations.create(
        start=0, end=1, footnote_node=ftnt_a.model)
    root['para_1'].footnotecitations.create(
        start=1, end=2, footnote_node=ftnt_b.model)
    root['list_1']['para_2'].footnotecitations.create(
        start=0, end=1, footnote_node=ftnt_c.model)

    def fts(cursor):
        meta_obj = meta.Meta(cursor, is_root=True, policy=policy)
        data = meta.MetaSerializer(
            meta_obj,
            context={'parent_serializer': DocCursorSerializer()},
        ).data
        return [node['identifier'] for node in data['descendant_footnotes']]

    assert fts(root) == ['root_1__footnote_a', 'root_1__para_1__footnote_b',
                         'root_1__list_1__para_3__footnote_c']
    assert fts(root['footnote_a']) == []
    assert fts(root['para_1']) == ['root_1__footnote_a',
                                   'root_1__para_1__footnote_b']
    assert fts(root['list_1']) == ['root_1__list_1__para_3__footnote_c']
    assert fts(root['list_1']['para_2']) == [
        'root_1__list_1__para_3__footnote_c']
    # no citations in para 3
    assert fts(root['list_1']['para_3']) == []


@pytest.mark.django_db
def test_table_of_contents():
    """The table of contents should be generated from titled elements,
    regardless of position in tree."""
    policy = mommy.make(Policy)
    root = DocCursor.new_tree('root', policy=policy)
    root.add_child('container', title='First title')
    root['container_1'].add_child('para')
    root['container_1']['para_1'].add_child('subpar')
    root['container_1']['para_1']['subpar_1'].add_child('item', title='Sub')
    root.add_child('other', title='Second')
    root.nested_set_renumber()

    data = meta.MetaSerializer(
        meta.Meta(root, is_root=True, policy=policy),
        context={'parent_serializer': DocCursorSerializer()},
    ).data
    assert data['table_of_contents'] == {
        'identifier': 'root_1',
        'title': '',
        'children': [
            {
                'identifier': 'root_1__container_1',
                'title': 'First title',
                'children': [{
                    'identifier': ('root_1__container_1__para_1__subpar_1'
                                   '__item_1'),
                    'title': 'Sub',
                    'children': [],
                }],
            }, {
                'identifier': 'root_1__other_1',
                'title': 'Second',
                'children': [],
            },
        ],
    }

    data = meta.MetaSerializer(
        meta.Meta(root['other_1'], is_root=False, policy=policy),
        context={'parent_serializer': DocCursorSerializer()},
    ).data
    assert 'table_of_contents' not in data
