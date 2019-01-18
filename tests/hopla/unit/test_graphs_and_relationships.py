from hopla.entities.entity import Entity
from hopla.graphs.graph import Graph
from hopla.relationships.core import Direction, Protection, RelationType
from hopla.relationships.relationship import Relationship


def test_graph():
    assert Graph(Entity())


def test_complex_graph():
    ids = ["A", "B", "C", "D", "E", "ROOT"]

    d_a = Entity(ids[0], core_id=ids[0])
    d_b = Entity(ids[1], core_id=ids[1])
    d_c = Entity(ids[2], core_id=ids[2])
    d_d = Entity(d_a, d_b, d_c, core_id=ids[3])
    d_e = Entity([{"D_d": d_d}], core_id=ids[4])
    root = Entity(d_e, core_id=ids[5])

    g = root.graph

    assert len(g.relationships) == 5
    assert g.entity.core_id == root.core_id
    assert g.entity != root
    assert len(g.entities_refs) == len(ids)
    assert len(g.relationships) == len(ids) - 1
    assert g.graph
    assert len(g.graph["__entities"]) == len(ids)
    assert len(g.graph["__relationships"]) == len(ids) - 1
    assert len(g.namespace_map) == len(ids)


def test_relationship():
    e_one = Entity(core_id="One")
    e_two = Entity(core_id="Two")

    rel = Relationship(e_one, e_two)

    assert rel.entity_1 == e_one
    assert rel.entity_2 == e_two
    assert rel.rel_type == Relationship.__name__.upper()
    assert rel.data == {}
    assert rel.safe == {}


def test_relationship_on_delete():
    e_one = Entity(core_id="One")
    e_two = Entity(core_id="Two")

    rel = Relationship(e_one, e_two)

    del e_one
    assert rel.entity_1 is None


def test_relationship_on_delete_preserve():
    e_one = Entity(core_id="One")
    e_two = Entity(core_id="Two")

    d_one = e_one.toDict()

    rel = Relationship(e_one, e_two, protection=Protection.PRESERVE)
    del e_one
    assert rel.safe['entity_1'] == d_one


def test_relationship_on_delete_cascade_delete():
    e_one = Entity(core_id="One")
    e_two = Entity(core_id="Two")

    rel = Relationship(e_one, e_two, protection=Protection.CASCADE_DELETE)
    del e_one
    assert rel.id is None
    assert rel.entity_1 is None
    assert rel.entity_2 is None
    assert rel.safe == {}
    assert rel.rel_type == RelationType.NONE.string
    assert rel.direction == Direction.NONE
    assert rel.protection == Protection.NONE


gc_collect_called = False
gc_collect_args = []


def test_relationship_on_delete_gc_collect():
    e_one = Entity(core_id="One")
    e_two = Entity(core_id="Two")

    def on_gc_collect(*args, **kwargs):
        global gc_collect_called
        global gc_collect_args

        gc_collect_called = True
        gc_collect_args = kwargs

    rel = Relationship(e_one, e_two, on_gc_collect=on_gc_collect)

    del e_one

    assert gc_collect_called
    assert gc_collect_args["relationship"] == rel


gc_collect_called = False


def test_relationship_on_delete_gc_collect_predominance_over_preserve():
    e_one = Entity(core_id="One")
    e_two = Entity(core_id="Two")

    def on_gc_collect(*args, **kwargs):
        global gc_collect_called
        gc_collect_called = True

    rel = Relationship(e_one, e_two, on_gc_collect=on_gc_collect, protection=Protection.PRESERVE)

    del e_one

    assert gc_collect_called
    assert rel.safe == {}


gc_collect_called = False


def test_relationship_on_delete_gc_collect_predominance_over_cascade_delete():
    e_one = Entity(core_id="One")
    e_two = Entity(core_id="Two")

    def on_gc_collect(*args, **kwargs):
        global gc_collect_called
        gc_collect_called = True

    rel = Relationship(e_one, e_two, on_gc_collect=on_gc_collect, protection=Protection.CASCADE_DELETE)

    del e_one

    assert gc_collect_called
    assert rel.safe == {}
    assert rel.id is not None
    assert rel.entity_1 is None
    assert rel.entity_2 is not None
    assert rel.safe == {}
    assert rel.rel_type != RelationType.NONE
    assert rel.direction == Direction.NONE
    assert rel.protection == Protection.CASCADE_DELETE


def test_link_operators():
    e1 = Entity("L1", core_id="L1")
    e2 = Entity("R1", core_id="R1")
    rel_none = e1 - e2

    assert type(rel_none) == Relationship
    assert rel_none.direction == Direction.NONE

    rel_left_right = e1 > e2

    assert type(rel_left_right) == Relationship
    assert rel_left_right.direction == Direction.LEFT_TO_RIGHT

    rel_right_left = e1 < e2

    assert type(rel_right_left) == Relationship
    assert rel_right_left.direction == Direction.RIGHT_TO_LEFT


def test_callable():
    e1 = Entity("L1", core_id="L1")
    e2 = Entity("R1", core_id="R1")
    rel = (e1 - e2)(rel_type="TYPE", protection=Protection.NONE, data=dict(a=2))

    assert type(rel) == Relationship
    assert rel.rel_type == "TYPE"
    assert rel.protection == Protection.NONE
    assert rel.data == dict(a=2)


def test_callable_change_protection():
    e1 = Entity("L1", core_id="L1")
    e2 = Entity("R1", core_id="R1")
    e3 = Entity("R3", core_id="R3")
    e4 = Entity("R4", core_id="R4")

    rel1 = e1 - e2

    assert rel1.protection == Protection.NONE
    del e2
    assert rel1.entity_2 is None

    rel2 = e1 - e3
    assert rel1.protection == Protection.NONE

    rel2 = rel2(protection=Protection.PRESERVE)
    assert rel2.protection == Protection.PRESERVE

    e3_dict = e3.toDict()
    del e3
    assert "entity_2" in rel2.safe.keys()
    assert rel2.safe["entity_2"] == e3_dict
