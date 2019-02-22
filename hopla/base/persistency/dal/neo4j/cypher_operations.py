from datetime import datetime

from neo4j.types.graph import Node as Neo4jNode

from hopla.base.collections import expand
from hopla.base.graphs.nodes.node import Node
from hopla.base.graphs.relationships.core import Direction
from hopla.base.persistency.drivers.neo4j.graph_db import NEO_INSTANCE
from hopla.base.persistency.generators.neo4j.graph_commands import GraphCommands
from hopla.base.persistency.generators.neo4j.node_commands import NodeCommands
from hopla.base.persistency.generators.neo4j.relationship_commands import RelationshipCommands
from hopla.base.persistency.operation import Operation, OperationType


class CypherOperations(object):
    database = NEO_INSTANCE

    @staticmethod
    def _execute(transaction):
        def run_transaction(transaction, command):
            result = transaction.run(command)
            return result

        results = []

        with CypherOperations.database.driver.session() as session:
            for operation in transaction:
                try:
                    cypher_transaction = session.write_transaction if operation.operation != OperationType.RETRIEVE \
                        else session.read_transaction
                    results.append(cypher_transaction(run_transaction, operation.command))
                except Exception as ex:
                    operation.data = ex
                    results.append(ex)
                CypherOperations.database.operations[datetime.utcnow().timestamp()] = operation

        return results

    @staticmethod
    def create_node(node, variable=None):
        create_node_operation = Operation(OperationType.CREATE,
                                          command=NodeCommands(node).self_generate_create(variable=variable))

        return CypherOperations._execute([create_node_operation])

    @staticmethod
    def merge_node(node, variable=None):
        create_node_operation = Operation(OperationType.CREATE,
                                          command=NodeCommands(node).self_generate_merge(variable=variable))

        return CypherOperations._execute([create_node_operation])

    @staticmethod
    def query_node(node_type=None, variable=None, **properties):
        results = []
        variable = str(variable) if variable is not None else "n"
        cypher_command = "{match} RETURN {variable}".format(
            match=NodeCommands.generate_match(variable=variable, node_type=node_type, **properties),
            variable=variable)

        cypher_results = CypherOperations._execute([Operation(OperationType.RETRIEVE, command=cypher_command)])

        results_data = [row for sub_results in [result.data() for result in cypher_results] for row in sub_results]

        if len(results_data) == 0:
            return results

        for data in results_data:
            result_value = data[variable]

            if type(result_value) != Neo4jNode:
                continue  # maybe raise exception here

            node_properties = {Node.properties_mapping[k]: v for k, v in expand(result_value).items()}

            results.append(Node(**node_properties))

        return results

    @staticmethod
    def node_exist(node, variable=None):
        variable = str(variable) if variable is not None else "n"

        cypher_command = "{match} RETURN {variable}".format(
            match=NodeCommands(node).self_generate_match(variable=variable, node_type=node.node_type),
            variable=variable)

        results = CypherOperations._execute([Operation(OperationType.RETRIEVE, command=cypher_command)])

        results_data = [row for sub_results in [result.data() for result in results] for row in sub_results]

        if len(results_data) == 0:
            return None

        result_value = results_data[0][variable]

        if type(result_value) != Neo4jNode:
            return None  # maybe raise exception here

        node_properties = {Node.properties_mapping[k]: v for k, v in expand(result_value).items()}
        node_properties["node_type"] = node.node_type
        print(node_properties)

        return Node(**node_properties) == node

    @staticmethod
    def query_relationship(variable=None, **properties):
        pass

    @staticmethod
    def get_relationship(node, variable=None):
        pass

    @staticmethod
    def create_relationship(relationship, variable=None):
        node1_var = "n1"
        node2_var = "n2"

        transaction = []

        nodes_merge_command = NodeCommands(relationship.node_1).self_generate_merge(variable=node1_var) + " " + \
                              NodeCommands(relationship.node_1).self_generate_merge(variable=node2_var)
        transaction.append(Operation(OperationType.CREATE,
                                     command=nodes_merge_command))

        transaction.append(Operation(OperationType.CREATE,
                                     command=RelationshipCommands(relationship).self_generate_create(
                                         variable=variable)))

        return CypherOperations._execute(transaction)

    @staticmethod
    def create_nodes_relationship(node1, node2, direction=None, variable=None, rel_type=None, **properties):
        if type(direction) != Direction:
            relationship = node1 > node2
        else:
            if direction == Direction.RIGHT_TO_LEFT:
                relationship = node1 < node2
            else:
                relationship = node1 > node2

        if rel_type is not None:
            relationship = relationship(rel_type=str(rel_type))
        if len(properties) > 0:
            relationship = relationship(data=properties)

        return CypherOperations.create_relationship(relationship, variable=variable)

    @staticmethod
    def delete_all():
        return CypherOperations._execute(Operation.create(OperationType.DELETE, commands=GraphCommands.delete_all()))

    @staticmethod
    def save_graph(graph):
        return CypherOperations._execute(
            Operation.create(OperationType.CREATE, commands=GraphCommands(graph).save_all()))
