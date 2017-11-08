import json
import random

import pytest
from django.test.utils import CaptureQueriesContext
from model_mommy import mommy

from document.models import DocNode
from document.serializers import DocCursorSerializer
from document.tests.utils import random_doc
from document.tree import DocCursor
from reqs.models import Policy, Requirement, Topic


@pytest.mark.django_db
@pytest.mark.urls('document.urls')
def test_404s(client):
    policy = mommy.make(Policy)
    root = DocCursor.new_tree('root', '0', policy=policy)
    root.add_child('sect')
    root.nested_set_renumber()
    DocNode.objects.bulk_create(n.model for n in root.walk())

    assert client.get("/987654321").status_code == 404
    assert client.get(f"/{policy.pk}").status_code == 200
    assert client.get(f"/{policy.pk}/root_0").status_code == 200
    assert client.get(f"/{policy.pk}/root_1").status_code == 404
    assert client.get(f"/{policy.pk}/root_0__sect_1").status_code == 200
    assert client.get(f"/{policy.pk}/root_0__sect_2").status_code == 404


@pytest.mark.django_db
@pytest.mark.urls('document.urls')
def test_correct_data(client):
    policy = mommy.make(Policy)
    root = DocCursor.new_tree('root', '0', policy=policy)
    sect1 = root.add_child('sect')
    root.add_child('sect')
    sect1.add_child('par', 'a')
    root.nested_set_renumber()
    DocNode.objects.bulk_create(n.model for n in root.walk())

    def result(url):
        return json.loads(client.get(url).content.decode('utf-8'))

    def serialize(node):
        return DocCursorSerializer(node, context={'policy': policy}).data

    assert result(f"/{policy.pk}") == serialize(root)
    assert result(f"/{policy.pk}/root_0") == serialize(root)
    assert result(f"/{policy.pk}/root_0__sect_1") == serialize(root['sect_1'])
    assert result(f"/{policy.pk}/root_0__sect_2") == serialize(root['sect_2'])
    assert result(f"/{policy.pk}/root_0__sect_1__par_a") \
        == serialize(root['sect_1']['par_a'])


@pytest.mark.django_db
@pytest.mark.urls('document.urls')
def test_by_pretty_url(client):
    policy = mommy.make(Policy, omb_policy_id='M-Something-18')
    root = DocCursor.new_tree('root', '0', policy=policy)
    root.nested_set_renumber()
    root.model.save()

    result = json.loads(client.get("/M-Something-18").content.decode("utf-8"))

    assert result == DocCursorSerializer(root,
                                         context={'policy': policy}).data


@pytest.mark.django_db
@pytest.mark.urls('document.urls')
def test_query_count(client):
    policy = mommy.make(Policy, omb_policy_id='M-O-A-R')
    root = random_doc(20, save=True, policy=policy, text='placeholder')
    subtree_nodes = {
        root.tree.nodes[idx]['model']
        for idx in root.tree.nodes()
        if idx != root.identifier
    }
    # select 5 nodes in the subtree as requirements
    req_nodes = random.sample(subtree_nodes, 5)
    reqs = mommy.make(Requirement, policy=policy, _quantity=5)

    for req_node, req in zip(req_nodes, reqs):
        for _ in range(random.randint(0, 4)):
            req.topics.add(mommy.make(Topic))
        req.docnode = req_node
        req.save()
    # select 3 nodes as footnotes
    for citing, footnote in zip(random.sample(subtree_nodes, 3),
                                random.sample(subtree_nodes, 3)):
        citing.footnotecitations.create(start=0, end=1, footnote_node=footnote)

    # pytest will alter the connection, so we only want to load it within this
    # test
    from django.db import connection
    with CaptureQueriesContext(connection) as capture:
        client.get("/M-O-A-R")
        # Query 1: Lookup the policy
        # 2: Lookup the root docnode, joining w/ req
        # 3: fetch footnote citations _and_ referenced node for the root
        # 4: fetch child nodes, joining w/ requirements
        # 5: fetch topics related to those requirements
        # 6: fetch footnote citations _and_ referenced node for child nodes
        assert len(capture) == 6
