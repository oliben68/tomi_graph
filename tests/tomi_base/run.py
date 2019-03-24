from tomi_graph.indexes_support import IndexesSupport

from tomi_graph.version_aware_entity import VersionAwareEntity

from tomi_graph.nodes.node_class import NodeBaseClass

from tomi_graph.entity_class_generator import EntityClassGenerator

NewClass = EntityClassGenerator(NodeBaseClass, VersionAwareEntity).create("NewClass", additional_fields=["field1"])

str_val = """{
    "__object":{
        "__UQ_NewClass":"NewClass:ada178c965454c509f74fe54be9a16b1",
        "__create_date":1553376154,
        "__data":null,
        "__encoding":"utf-8",
        "__id":"ada178c965454c509f74fe54be9a16b1",
        "__key":null,
        "__name":null,
        "__ttl":-1,
        "__update_date":1553376154,
        "__version":0,
        "field1":1
    },
    "__type":"NewClass"
}"""

restored = NewClass.from_str(str_val)
classname = "NewNode"
# indexes = {"index": ["id"]}
#
# new_node = EntityClassGenerator(NodeBaseClass, VersionAwareEntity, IndexesSupport).create(entity_type=classname,
#                                                                                           indexes=indexes)
#
# assert new_node.__name__ == classname
# assert hasattr(new_node, "indexes")
# assert hasattr(new_node, IndexesSupport.INDEXES_CLASS_METHOD)
#
# assert len(new_node().indexes) == len(indexes) + 1
# assert len(getattr(new_node, IndexesSupport.INDEXES_CLASS_METHOD)()) == len(indexes)