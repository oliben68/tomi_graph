from tomi_graph.entity_class_generator import EntityClassGenerator
from tomi_graph.indexes_support import IndexesSupport
from tomi_graph.nodes.node_class import NodeBaseClass
from tomi_graph.version_aware_entity import VersionAwareEntity


def test_node_valid_indexes():
    classname = "NewNode"
    indexes = {"index": ["core_id"]}

    new_node = EntityClassGenerator(NodeBaseClass, VersionAwareEntity, IndexesSupport).create(entity_type=classname,
                                                                                              indexes=indexes)

    assert new_node.__name__ == classname
    assert hasattr(new_node, "indexes")
    assert hasattr(new_node, IndexesSupport.INDEXES_CLASS_METHOD)

    assert len(new_node().indexes) == len(indexes) + 1
    assert len(getattr(new_node, IndexesSupport.INDEXES_CLASS_METHOD)()) == len(indexes)


def test_node_invalid_index():
    classname = "NewNode"
    indexes = {"index": [""]}

    new_node = EntityClassGenerator(NodeBaseClass, VersionAwareEntity, IndexesSupport).create(entity_type=classname,
                                                                                              indexes=indexes)

    assert new_node.__name__ == classname
    assert hasattr(new_node, "indexes")
    assert hasattr(new_node, IndexesSupport.INDEXES_CLASS_METHOD)

    assert len(new_node().indexes) == 1
    assert len(getattr(new_node, IndexesSupport.INDEXES_CLASS_METHOD)()) == 0
