from hopla_graph.collections import flatten
from hopla_graph.graphs.relationships.core import Direction
from hopla_graph.graphs.relationships.relationship import Relationship
from hopla_graph.persistency.generators.neo4j.cypher_commands import CypherCommands
from hopla_graph.persistency.generators.neo4j.node_commands import NodeCommands


class RelationshipCommands(CypherCommands):
    entity_type = Relationship

    @staticmethod
    def cypher_direction_command(direction):
        if type(direction) == str:
            try:
                direction = Direction.__members__[direction]
            except KeyError:
                return "-[{relationship}]->"

        if not type(direction) == Direction:
            return "-[{relationship}]->"

        if direction == Direction.RIGHT_TO_LEFT:
            return "<-[{relationship}]-"
        else:
            return "-[{relationship}]->"

    @staticmethod
    def _create_command(verb, variable=None, entity_type=None, **properties):
        node1_var = "n1"
        node2_var = "n2"

        variable = variable if variable is not None else "r"

        match1 = NodeCommands.generate_match(node1_var, excluded=["__type"], **properties["__node_1"])
        match2 = NodeCommands.generate_match(node2_var, excluded=["__type"], **properties["__node_2"])
        match_command = match1 + "," + match2.replace("MATCH", "")

        if entity_type is not None:
            properties["__rel_type"] = entity_type

        properties_data = {k: v for k, v in properties.items() if
                           k not in ["__direction", "__rel_type", "__node_1", "__node_2"]}
        relationship_props = CypherCommands.properties_values_map(
            **{k: v for k, v in flatten(properties_data).items() if str(v).upper() != "NONE"})

        definition = variable + (":" + str(properties["__rel_type"]) if "__rel_type" in properties.keys() else "")

        connector = RelationshipCommands.cypher_direction_command(properties["__direction"]).format(
            relationship=" ".join([definition, relationship_props]))

        create_command = "{verb} ({node1}){connector}({node2})".format(verb=verb,
                                                                       node1=node1_var,
                                                                       node2=node2_var,
                                                                       connector=connector)

        return_command = "RETURN " + ", ".join([variable, node1_var, node2_var])

        return " ".join([match_command, create_command, return_command])

    @staticmethod
    def generate_create(variable=None, entity_type=None, **properties):
        return RelationshipCommands._create_command("CREATE", variable=variable, entity_type=entity_type, **properties)

    def self_generate_create(self, variable=None):
        create_command = RelationshipCommands.generate_create(variable=variable, entity_type=self.entity.rel_type,
                                                              **self.entity.toDict())
        return create_command

    @staticmethod
    def generate_merge(variable=None, entity_type=None, **properties):
        return RelationshipCommands._create_command("MERGE", variable=variable, entity_type=entity_type, **properties)

    def self_generate_merge(self, variable=None):
        merge_command = RelationshipCommands.generate_merge(variable=variable, entity_type=self.entity.rel_type,
                                                            **self.entity.toDict())
        return merge_command

    @staticmethod
    def generate_match(node, variable=None):
        pass

    def self_generate_match(self, variable=None):
        pass

    @staticmethod
    def generate_where(boolean_operator=None, excluded=None, **kwargs):
        pass

    def self_generate_where(self, boolean_operator=None, excluded=None):
        pass
