from hopla.base.graphs.indexes_support import IndexesSupport
from hopla.base.graphs.nodes.node_class import NodeClassGenerator


def test_node_valid_indexes():
    classname = "NewNode"
    indexes = {"index": ["core_id"]}

    NewNode = NodeClassGenerator.create(entity_type=classname, indexes=indexes)

    assert NewNode.__name__ == classname
    assert hasattr(NewNode, "indexes")
    assert hasattr(NewNode, IndexesSupport.INDEXES_CLASS_METHOD)

    assert len(NewNode().indexes) == len(indexes) + 1
    assert len(getattr(NewNode, IndexesSupport.INDEXES_CLASS_METHOD)()) == len(indexes)


def test_node_invalid_index():
    classname = "NewNode"
    indexes = {"index": [""]}

    NewNode = NodeClassGenerator.create(entity_type=classname, indexes=indexes)

    assert NewNode.__name__ == classname
    assert hasattr(NewNode, "indexes")
    assert hasattr(NewNode, IndexesSupport.INDEXES_CLASS_METHOD)

    assert len(NewNode().indexes) == 1
    assert len(getattr(NewNode, IndexesSupport.INDEXES_CLASS_METHOD)()) == 0

