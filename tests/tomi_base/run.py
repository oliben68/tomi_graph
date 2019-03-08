from tomi_base.graphs.nodes.node_class import NodeBaseClass
from tomi_base.graphs.entity_class_generator import EntityClassGenerator
from tomi_base.graphs.version_aware_entity import VersionAwareEntity
from tomi_base.graphs.indexes_support import IndexesSupport

from tomi_data.persistency.generators.cypher.graph_commands import GraphCommands

NodeTest = EntityClassGenerator(NodeBaseClass, VersionAwareEntity, IndexesSupport).create("NodeTest")

d_e = NodeTest(core_id="E")
root = NodeTest(d_e, core_id="Root")
g = root.graph