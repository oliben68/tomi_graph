from neobolt.exceptions import ServiceUnavailable
from hopla.persistency.operation import Operation, Operations

try:
    from hopla.config import DB_CONFIG
except ImportError:
    from hopla.config.defaults import DB_CONFIG
from neo4j import GraphDatabase


class GraphDb(object):
    def __init__(self):
        init_operation = Operation(Operations.INIT)
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

