import warnings
from ujson import dumps
from uuid import uuid4

# import pytest
# from pydispatch import dispatcher
from testfixtures import LogCapture

from hopla.entities.core import DEFAULT_ENCODING
from hopla.entities.entity import Entity
from hopla.entities.exceptions import CoreDocumentException, EncodingWarning, CircularReferenceWarning, \
    SchemaValidationWarning, SchemaValidationException
from hopla.events.dispatcher import connect_handler, disconnect_handler
from hopla.events.exceptions import HandlerArgsCountException
from hopla.events.signals import Signals

from hopla.graphs.graph import Graph
from hopla.relationships.relationship import Relationship
from hopla.validation.validator import Validator

from hopla.collections import flatten, expand

e1 = Entity("E1", core_id="E1")
e2 = Entity("E2", core_id="E2")
e3 = Entity("E3", core_id="E3")

g = Graph(Graph.NAMESPACE_DELIMITER)

g.add_entity(e1)
g.add_relationship(Relationship(e2, e3))

g_entities_count = len(g.entities)
g_relationships_count = len(g.relationships)
assert g_entities_count == 3
assert g_relationships_count == 1

ids = ["A", "B", "C", "D", "E", "ROOT"]

d_a = Entity(ids[0], core_id=ids[0])
d_b = Entity(ids[1], core_id=ids[1])
d_c = Entity(ids[2], core_id=ids[2])
d_d = Entity(d_a, d_b, d_c, core_id=ids[3])
d_e = Entity([{"D_d": d_d}], core_id=ids[4])
root = Entity(d_e, core_id=ids[5])

rels = root.graph.toDict()["__relationships"]

f = flatten(rels)
f