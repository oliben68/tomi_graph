from neobolt.exceptions import ServiceUnavailable

try:
    from hopla.config import DB_CONFIG
except ImportError:
    from hopla.config.defaults import DB_CONFIG
from neo4j import GraphDatabase

# driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "123456"))


class GraphDb(object):
    def __init__(self):
        self._driver = None
        self._current_exception = None
        try:
            self._driver = GraphDatabase.driver(
                "{protocol}://{host}:{port}".format(protocol=DB_CONFIG["server"]["protocol"], host=DB_CONFIG["server"]["host"],
                                                    port=DB_CONFIG["server"]["port"]),
                auth=(DB_CONFIG["user"]["name"], DB_CONFIG["user"]["password"]))
        except ServiceUnavailable as ex:
            self._current_exception = ex
            raise

