from collections.abc import MutableSequence

from hopla_graph.collections import flatten
from hopla_graph.graphs.nodes.node import Node
from hopla_graph.persistency.generators.neo4j.cypher_commands import CypherCommands
#from hopla_graph.persistency.generators.neo4j.relationship_commands import RelationshipCommands


class NodeCommands(CypherCommands):
    entity_type = Node
    excluded_properties = ["__type"]
    property_prefix = "__object."

    def __init__(self, entity):
        super().__init__(entity)

    @staticmethod
    def _create_command(verb, variable, node_type=None, **properties):
        props = {k: v for k, v in properties.items() if v is not None}
        if node_type is None:
            if "__type" in props.keys():
                if len(str(props["__type"])) > 0:
                    node_type = str(props["__type"])
                else:
                    node_type = NodeCommands.entity_type.__name__
            else:
                node_type = NodeCommands.entity_type.__name__
        variable_name = node_type[0].lower() if variable is None else str(variable)
        cypher = ("CREATE" if verb == "CREATE" else "MERGE") + "({name}:{type} {properties})"
        props = CypherCommands.properties_values_map(excluded=NodeCommands.excluded_properties,
                                                     property_prefix=NodeCommands.property_prefix,
                                                     **props)

        return cypher.format(name=variable_name, type=node_type, properties=props)

    @staticmethod
    def generate_match(variable=None, excluded=None, node_type=None, **properties):
        props = {k: v for k, v in properties.items() if v is not None}
        if node_type is None and "__type" in props.keys() and len(str(props["__type"])) > 0:
            node_type = str(props["__type"])
        if node_type is not None:
            variable_name = node_type[0].lower() if variable is None else str(variable)
        else:
            variable_name = str(variable) if variable is not None else "n"

        excluded = [] if excluded is None else excluded
        query_props = CypherCommands.properties_values_map(excluded=excluded,
                                                           property_prefix=NodeCommands.property_prefix,
                                                           **flatten(props))
        if node_type is not None:
            return "MATCH ({name}:{type} {properties})".format(name=variable_name, type=node_type,
                                                               properties=query_props)
        else:
            return "MATCH ({name} {properties})".format(name=variable_name, properties=query_props)

    def self_generate_match(self, variable=None, excluded=None, node_type=None):
        excluded = list(excluded) if isinstance(excluded, MutableSequence) or type(excluded) in (set, tuple) else []
        excluded = list(set(NodeCommands.excluded_properties + excluded))
        node_type = self.entity_type.__name__ if node_type is None else str(node_type)
        return NodeCommands.generate_match(variable=variable, excluded=excluded, node_type=node_type,
                                           **flatten(self.entity.toDict()))

    @staticmethod
    def generate_create(variable=None, entity_type=None, **properties):
        command = NodeCommands._create_command("CREATE", variable, **flatten(properties))
        return command

    def self_generate_create(self, variable=None):
        return NodeCommands.generate_create(variable, **flatten(self.entity.toDict()))

    @staticmethod
    def generate_merge(variable=None, entity_type=None, **properties):
        command = NodeCommands._create_command("MERGE", variable, **flatten(properties))
        return command

    def self_generate_merge(self, variable=None):
        return NodeCommands.generate_merge(variable, **flatten(self.entity.toDict()))

    @staticmethod
    def generate_where(boolean_operator=None, excluded=None, **properties):
        return "WHERE " + CypherCommands.properties_values_list(boolean_operator=boolean_operator, excluded=excluded,
                                                                **properties)

    def self_generate_where(self, boolean_operator=None, excluded=None):
        return CypherCommands.generate_where(boolean_operator=boolean_operator, excluded=excluded,
                                             **flatten(self.entity.toDict()))
