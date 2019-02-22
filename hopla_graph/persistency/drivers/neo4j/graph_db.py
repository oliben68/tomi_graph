from neobolt.exceptions import ServiceUnavailable

from hopla_graph.shared.meta_singleton import MetaSingleton
from hopla_graph.persistency.operation import Operation, OperationType

try:
    from hopla_graph.config import DB_CONFIG
except ImportError:
    from hopla_graph.config.defaults import DB_CONFIG
from neo4j import GraphDatabase


class GraphDb(metaclass=MetaSingleton):
    @property
    def driver(self):
        return self._driver

    @property
    def operations(self):
        return self._operations

    def __init__(self):
        init_operation = Operation(OperationType.INIT)
        self._driver = None
        self._operations = {}
        try:
            self._driver = GraphDatabase.driver(
                "{protocol}://{host}:{port}".format(protocol=DB_CONFIG["server"]["protocol"],
                                                    host=DB_CONFIG["server"]["host"],
                                                    port=DB_CONFIG["server"]["port"]),
                auth=(DB_CONFIG["user"]["name"], DB_CONFIG["user"]["password"]))
        except ServiceUnavailable as ex:
            init_operation.data = ex
        self._operations[init_operation.timestamp] = init_operation


NEO_INSTANCE = GraphDb()
