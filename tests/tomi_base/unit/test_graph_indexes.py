from tomi_base.base.graphs.entity_class_generator import EntityClassGenerator
from tomi_base.base.graphs.indexes_support import IndexesSupport
from tomi_base.base.graphs.nodes.node_class import NodeBaseClass
from tomi_base.base.graphs.version_aware_entity import VersionAwareEntity


def test_node_valid_indexes():
    classname = "NewNode"
    indexes = {"index": ["core_id"]}

    NewNode = EntityClassGenerator(NodeBaseClass, VersionAwareEntity, IndexesSupport).create(entity_type=classname,
                                                                                             indexes=indexes)

    assert NewNode.__name__ == classname
    assert hasattr(NewNode, "indexes")
    assert hasattr(NewNode, IndexesSupport.INDEXES_CLASS_METHOD)

    assert len(NewNode().indexes) == len(indexes) + 1
    assert len(getattr(NewNode, IndexesSupport.INDEXES_CLASS_METHOD)()) == len(indexes)


def test_node_invalid_index():
    classname = "NewNode"
    indexes = {"index": [""]}

    NewNode = EntityClassGenerator(NodeBaseClass, VersionAwareEntity, IndexesSupport).create(entity_type=classname,
                                                                                             indexes=indexes)

    assert NewNode.__name__ == classname
    assert hasattr(NewNode, "indexes")
    assert hasattr(NewNode, IndexesSupport.INDEXES_CLASS_METHOD)

    assert len(NewNode().indexes) == 1
    assert len(getattr(NewNode, IndexesSupport.INDEXES_CLASS_METHOD)()) == 0
