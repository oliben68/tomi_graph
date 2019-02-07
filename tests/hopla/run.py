# import pytest
# from pydispatch import dispatcher

from hopla.graphs.nodes.node import Node

from hopla.graphs.graphs.graph import Graph
from hopla.graphs.relationships.relationship import Relationship

from hopla.collections import flatten

e1 = Node("E1", core_id="E1")
e2 = Node("E2", core_id="E2")
e3 = Node("E3", core_id="E3")

g = Graph(Graph.NAMESPACE_DELIMITER)

g.add_entity(e1)
g.add_relationship(Relationship(e2, e3))

g_entities_count = len(g.entities)
g_relationships_count = len(g.relationships)
assert g_entities_count == 3
assert g_relationships_count == 1

ids = ["A", "B", "C", "D", "E", "ROOT"]

d_a = Node(ids[0], core_id=ids[0])
d_b = Node(ids[1], core_id=ids[1])
d_c = Node(ids[2], core_id=ids[2])
d_d = Node(d_a, d_b, d_c, core_id=ids[3])
d_e = Node([{"D_d": d_d}], core_id=ids[4])
root = Node(d_e, core_id=ids[5])

rels = root.graph.toDict()["__relationships"]

f = flatten(rels)
f