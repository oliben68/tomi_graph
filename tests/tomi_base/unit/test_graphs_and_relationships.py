from tomi_graph.graphs.graph import Graph
from tomi_graph.graphs.node_data_graph import NodeDataGraph
from tomi_graph.nodes.node_class import NodeBaseClass
from tomi_graph.relationships.core.direction import Direction
from tomi_graph.relationships.relationship_class import Relationship, RelationshipBaseClass


def test_graph():
    assert NodeDataGraph(NodeBaseClass())


def test_complex_graph():
    ids = ["A", "B", "C", "D", "E", "ROOT"]

    d_a = NodeBaseClass(ids[0], core_id=ids[0])
    d_b = NodeBaseClass(ids[1], core_id=ids[1])
    d_c = NodeBaseClass(ids[2], core_id=ids[2])
    d_d = NodeBaseClass(d_a, d_b, d_c, core_id=ids[3])
    d_e = NodeBaseClass([{"D_d": d_d}], core_id=ids[4])
    root = NodeBaseClass(d_e, core_id=ids[5])

    g = root.graph

    assert len(g.relationships) == 5
    assert g.root_node.core_id == root.core_id
    assert g.root_node != root
    assert len(g.nodes) == len(ids)
    assert len(g.relationships) == len(ids) - 1
    assert g.dictionary
    assert len(g.dictionary["__nodes"]) == len(ids)
    assert len(g.dictionary["__relationships"]) == len(ids) - 1
    assert len(g.namespace_map) == len(ids)


def test_relationship():
    e_one = NodeBaseClass(core_id="One")
    e_two = NodeBaseClass(core_id="Two")

    rel = Relationship(e_one, e_two)

    assert rel.node_1 == e_one
    assert rel.node_2 == e_two
    assert rel.rel_type == RelationshipBaseClass.__name__
    assert rel.data == {}


def test_link_operators():
    e1 = NodeBaseClass("L1", core_id="L1")
    e2 = NodeBaseClass("R1", core_id="R1")
    rel_none = e1 - e2

    assert type(rel_none).__name__ == RelationshipBaseClass.__name__
    assert rel_none.direction == Direction.NONE

    rel_left_right = e1 > e2

    assert type(rel_left_right).__name__ == RelationshipBaseClass.__name__
    assert rel_left_right.direction == Direction.LEFT_TO_RIGHT

    rel_right_left = e1 < e2

    assert type(rel_right_left).__name__ == RelationshipBaseClass.__name__
    assert rel_right_left.direction == Direction.RIGHT_TO_LEFT


def test_link_multiple_operators():
    e1 = NodeBaseClass("E1", core_id="E1")
    e2 = NodeBaseClass("E2", core_id="E2")
    e3 = NodeBaseClass("E3", core_id="E3")

    g1 = e1 - e2 - e3

    assert type(g1) == Graph
    assert len(g1.nodes) == 3
    assert len(g1.relationships) == 2

    g2 = e1 > (e2 > e3)

    assert type(g2) == Graph
    assert len(g2.nodes) == 3
    assert len(g2.relationships) == 2

    g3 = e1 < (e2 < e3)

    assert type(g3) == Graph
    assert len(g3.nodes) == 3
    assert len(g3.relationships) == 2

    rel_first = e2 > e3
    g4 = e1 < rel_first

    assert type(rel_first).__name__ == RelationshipBaseClass.__name__
    assert type(g4) == Graph
    assert len(g4.nodes) == 3
    assert len(g4.relationships) == 2


def test_mix_types_operations():
    e1 = NodeBaseClass("E1", core_id="E1")
    e2 = NodeBaseClass("E2", core_id="E2")
    e3 = NodeBaseClass("E3", core_id="E3")
    e4 = NodeBaseClass("E4", core_id="E4")
    e5 = NodeBaseClass("E5", core_id="E5")
    e6 = NodeBaseClass("E6", core_id="E6")

    g1 = e1 - e2 - e3
    g5 = g1 + e4
    assert type(g5) == Graph
    assert e4.core_id in g5.isolates
    assert len(g5.nodes) == 4
    assert len(g5.relationships) == 2

    r1 = e1 - e2
    assert type(r1).__name__ == RelationshipBaseClass.__name__
    g6 = e3 - e4 - e5
    assert type(g6) == Graph
    g6 = g6 + r1
    assert type(g6) == Graph
    assert len(g6.nodes) == 5
    assert len(g6.relationships) == 3

    g7 = e1 - e2 - e3
    g8 = e4 - e5 - e6
    assert type(g7) == Graph
    assert type(g8) == Graph
    g9 = g7 + g8
    assert type(g9) == Graph
    assert len(g9.relationships) == len(g7.relationships) + len(g8.relationships)
    assert set(g9.nodes.keys()) == set(list(g7.nodes.keys()) + list(g8.nodes.keys()))


def test_adding_entity_graph():
    ids = ["A", "B", "C", "D", "E", "ROOT"]

    d_a = NodeBaseClass(ids[0], core_id=ids[0])
    d_b = NodeBaseClass(ids[1], core_id=ids[1])
    d_c = NodeBaseClass(ids[2], core_id=ids[2])
    d_d = NodeBaseClass(d_a, d_b, d_c, core_id=ids[3])
    d_e = NodeBaseClass([{"D_d": d_d}], core_id=ids[4])
    root = NodeBaseClass(d_e, core_id=ids[5])

    g1 = root.graph

    e1 = NodeBaseClass("E1", core_id="E1")
    e2 = NodeBaseClass("E2", core_id="E2")
    e3 = NodeBaseClass("E3", core_id="E3")

    g2 = e1 - e2 - e3

    g3 = g1 + g2
    assert type(g3) == Graph
    assert len(g3.relationships) == len(g1.relationships) + len(g2.relationships)
    assert set(g3.nodes.keys()) == set(list(g1.nodes.keys()) + list(g2.nodes.keys()))


def test_callable():
    e1 = NodeBaseClass("L1", core_id="L1")
    e2 = NodeBaseClass("R1", core_id="R1")
    rel = e1 - e2
    new_data = dict(a=2)
    rel(data=new_data)

    assert type(rel).__name__ == RelationshipBaseClass.__name__ == rel.rel_type
    assert rel.data == new_data


def test_callable_new_type():
    e1 = NodeBaseClass("L1", core_id="L1")
    e2 = NodeBaseClass("R1", core_id="R1")
    new_type = "NewType"
    rel = (e1 - e2)(rel_type=new_type)

    assert type(rel).__name__ != RelationshipBaseClass.__name__
    assert rel.rel_type == new_type


def test_graph_methods():
    e1 = NodeBaseClass("E1", core_id="E1")
    e2 = NodeBaseClass("E2", core_id="E2")
    e3 = NodeBaseClass("E3", core_id="E3")

    g = Graph(Graph.NAMESPACE_DELIMITER)

    g.add_node(e1)
    g.add_relationship(Relationship(e2, e3))

    g_entities_count = len(g.nodes)
    g_relationships_count = len(g.relationships)
    assert g_entities_count == 3
    assert g_relationships_count == 1

    e4 = NodeBaseClass("E4", core_id="E4")
    e5 = NodeBaseClass("E5", core_id="E5")
    e6 = NodeBaseClass("E6", core_id="E6")

    g2 = Graph(Graph.NAMESPACE_DELIMITER)

    g2.add_relationship(Relationship(e4, e5))
    g2.add_relationship(e5 - e6)

    assert len(g2.nodes) == 3
    assert len(g2.relationships) == 2

    g.add_graph(g2)

    assert len(g.nodes) == len(g2.nodes) + g_entities_count
    assert len(g.relationships) == len(g2.relationships) + g_relationships_count
