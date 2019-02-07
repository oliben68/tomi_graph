import uuid
import warnings
from copy import deepcopy
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import TextIOBase
from ujson import loads, load, dumps

import chardet
from hopla.graphs.graphs.entity_graph import EntityGraph
from objectpath import Tree
from py._path.local import LocalPath

from hopla.graphs.operators import GraphOperationDirection, GraphOperation
from hopla.graphs.operators.operator_resolver import OperatorsResolver
from hopla.graphs.entities.core import BUILT_INS, DEFAULT_ENCODING
from hopla.graphs.entities.core.entity import BaseEntity
from hopla.graphs.entities.exceptions import CoreDocumentException, EncodingWarning, CircularReferenceWarning
from hopla.events import dispatcher
from hopla.events.signals import Signals
from hopla.graphs.graphs.graph import Graph
from hopla.logging.auto.logging import auto_log
from hopla.graphs.relationships.core import Direction
from hopla.graphs.relationships.relationship import Relationship


class Entity(OperatorsResolver, BaseEntity):
    @property
    def entity_type(self):
        return self._entity_type

    @property
    def core_id(self):
        return self._core_id

    @property
    def key(self):
        return self._key

    @property
    def encoding(self):
        return self._encoding

    @property
    def name(self):
        return self._name

    @name.setter
    @auto_log()
    def name(self, value):
        if type(value) == str:
            self._name = value
        else:
            raise CoreDocumentException("name property is of type str!")

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    @auto_log()
    def ttl(self, value):
        try:
            self._ttl = Decimal(value)
        except InvalidOperation:
            raise CoreDocumentException("ttl property should be a number!")

    @property
    def options(self):
        return self._options

    def get_data(self):
        return self._inner_data

    @property
    def create_date(self):
        return self._create_date

    @property
    def update_date(self):
        return self._update_date

    @property
    def validator(self):
        return self._validator

    @property
    def graph(self):
        if self._graph is None:
            self._graph = EntityGraph(self)
        return self._graph

    @auto_log()
    def set_data(self, data, raise_event=True):
        cached_value = None if self._new else self._inner_data
        if type(data) == str or type(data) == bytes:
            if type(data) == bytes:
                encoding = chardet.detect(data)["encoding"]
                if chardet.detect(data)["encoding"].lower() != self._encoding.lower():
                    warnings.warn(
                        EncodingWarning("Detected encoding {d} is different from entity encoding {e}.".format(
                            d=encoding, e=self._encoding)))
                    self._encoding = encoding.lower()
                    data = data.decode(encoding)
                else:
                    data = data.decode(self._encoding)
            self._inner_data = data
        elif type(data) in BUILT_INS and type(data) != tuple:
            self._inner_data = data
        elif type(data) == tuple:
            self._inner_data = list(data)
        elif type(data) == TextIOBase or type(data) == LocalPath:
            try:
                self._inner_data = load(data)
            except Exception as ex:
                raise CoreDocumentException(ex)
        else:
            self._inner_data = data

        try:
            _ = str(self)
        except RecursionError:
            warnings.warn(CircularReferenceWarning("Circular reference detected."))

        if not self._new:
            self._update_date = int(datetime.utcnow().timestamp())
            if raise_event:
                dispatcher.send_message(
                    message={
                        "type": Signals.ENTITY_UPDATED,
                        "entity": self,
                        "changes": {
                            "from": cached_value,
                            "to": self._inner_data
                        }},
                    signal=Signals.ENTITY_UPDATED,
                    sender=object())

    def bypass_update_date(self):
        """

        :return:
        """
        self._new = True

    def __init__(self, *args, entity_type=None, core_id=None, encoding=None, key=None, name=None, data=None, ttl=-1,
                 validator=None, options=None, raise_event=None):
        """

        :param args:
        :param entity_type:
        :param core_id:
        :param encoding:
        :param key:
        :param name:
        :param data:
        :param options:
        :raise_event:
        """
        self._entity_type = Entity.__name__ if entity_type is None else str(entity_type)
        self._core_id = uuid.uuid4().hex if core_id is None else str(core_id)
        self._encoding = DEFAULT_ENCODING if type(encoding) != str else encoding
        self._key = key
        self._name = name
        self._inner_data = None
        self._ttl = ttl
        self._options = options
        self._new = True
        self._create_date = int(datetime.utcnow().timestamp())
        self._update_date = self._create_date
        self._validator = validator
        self._graph = None

        if data is None:
            if len(args) == 1:
                self.set_data(args[0])
            elif len(args) > 1:
                self.set_data(args)
            else:
                self.set_data(None)
        else:
            self.set_data(data)

        if raise_event or raise_event is None:
            dispatcher.send_message(
                message={
                    "type": Signals.ENTITY_CREATED,
                    "entity": self},
                signal=Signals.ENTITY_CREATED,
                sender=object())
        self._new = False

    def __str__(self):
        return BaseEntity.serialize_to_string(self.toDict())  # dumps(self.toDict(), **(dict(indent=4, sort_keys=True)))

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    @staticmethod
    def _to_dict(o):
        def dict_format(d):
            return {
                "__type": d.entity_type,
                "__object": {
                    "__id": d.core_id,
                    "__name": d.name,
                    "__key": str(d.key) if d.key is not None else None,
                    "__encoding": d.encoding,
                    "__create_date": d.create_date,
                    "__update_date": d.update_date,
                    "__ttl": d.ttl,
                    "__data": Entity._to_dict(d.get_data()),
                }
            }

        if type(o) == str:
            return o
        try:
            _ = iter(o)
            if issubclass(type(o), dict) or type(o) == dict:
                for k, v in o.items():
                    if issubclass(type(v), BaseEntity):
                        o[k] = dict_format(v)
                    else:
                        o[k] = Entity._to_dict(v)
            elif issubclass(type(o), list) or type(o) == list:
                for idx, v in enumerate(o):
                    if issubclass(type(v), BaseEntity):
                        o[idx] = dict_format(v)
                    else:
                        o[idx] = Entity._to_dict(v)
            return o
        except TypeError:
            if issubclass(type(o), BaseEntity):
                return dict_format(o)
            else:
                return o

    def children(self):
        tree = Tree(loads(str(self)))
        return [Entity.from_str(dumps(d["__object"])) for d in
                list(tree.execute('$..*[@.__type and @.__object]')) if
                d["__object"]["__id"] != self.core_id]

    def toDict(self):
        return Entity._to_dict(deepcopy(self))

    def clone(self, new=None, raise_event=True):
        cloned = deepcopy(self)

        new_instance = new if type(new) == bool else False
        cloned._create_date = int(datetime.utcnow().timestamp()) if new_instance else cloned.create_date
        cloned._update_date = cloned._create_date if new_instance else cloned.update_date
        cloned._ttl = -1 if new_instance else cloned.ttl

        if raise_event:
            dispatcher.send_message(dict(type=Signals.ENTITY_CLONED, entity=cloned, source=self),
                                    Signals.ENTITY_CLONED)
        return cloned

    @staticmethod
    def from_str(string_value, new=None):
        new_instance = new if type(new) == bool else False
        o = loads(string_value)

        if type(o) == dict and {"__type", "__object"} == set(o.keys()):
            return Entity.from_str(dumps(o["__object"]), new=new_instance)

        if type(o) == dict and {"__id", "__name", "__key", "__encoding", "__create_date", "__update_date",
                                "__data", "__ttl"} == set(o.keys()):
            core_id = str(uuid.uuid4()) if new_instance else o["__id"]
            doc = Entity(o["__data"], core_id=core_id,
                         encoding=o["__encoding"], key=o["__key"], name=o["__name"])

            if type(o["__data"]) == dict and {"__object", "__type"} == set(o["__data"].keys()):
                doc.set_data(Entity.from_str(dumps(o["__data"]["__object"]), new=new_instance))
            else:
                doc.set_data(Entity.from_str(dumps(o["__data"])))

            doc._create_date = int(datetime.utcnow().timestamp()) if new_instance else o["__create_date"]
            doc._update_date = doc._create_date if new_instance else o["__update_date"]
            doc._ttl = -1 if new_instance else o["__ttl"]

            return doc

        if type(o) == dict and {"__id", "__name", "__key", "__encoding", "__create_date", "__update_date",
                                "__data", "__ttl"} != set(o.keys()):
            return {k: Entity.from_str(dumps(v), new=new_instance) for k, v in o.items()}

        if type(o) == list:
            return [Entity.from_str(dumps(sub_o), new=new_instance) for sub_o in o]
        return o

    def __repr__(self):
        # In some corner cases __repr__ gets called before __init__
        try:
            return "<type '{klass}' - value {value}>".format(klass=self.entity_type, value=dumps(self.toDict()))
        except AttributeError:
            return super().__repr__()

    def operation_resolution(self, other, operation, direction):
        if operation == GraphOperation.LINK:
            operator = "-"
            if direction == GraphOperationDirection.ENTITY_ENTITY:
                return Relationship(self, other, direction=Direction.NONE)
            if direction == GraphOperationDirection.ENTITY_RELATIONSHIP:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_entity(self)
                graph.add_relationship(other)
                graph.add_relationship(Relationship(self, other.entity_2))
                return graph
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name__,
                                                                                            other=type(other).__name__))
        if operation == GraphOperation.LINK_LEFT_RIGHT:
            operator = ">"
            if direction == GraphOperationDirection.ENTITY_ENTITY:
                return Relationship(self, other, direction=Direction.LEFT_TO_RIGHT)
            if direction == GraphOperationDirection.ENTITY_RELATIONSHIP:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_entity(self)
                graph.add_relationship(other)
                graph.add_relationship(Relationship(self, other.entity_2, direction=Direction.LEFT_TO_RIGHT))
                return graph
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name__,
                                                                                            other=type(other).__name))
        if operation == GraphOperation.LINK_RIGHT_LEFT:
            operator = "<"
            if direction == GraphOperationDirection.ENTITY_ENTITY:
                return Relationship(self, other, direction=Direction.RIGHT_TO_LEFT)
            if direction == GraphOperationDirection.ENTITY_RELATIONSHIP:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_entity(self)
                graph.add_relationship(other)
                graph.add_relationship(Relationship(self, other.entity_2, direction=Direction.RIGHT_TO_LEFT))
                return graph
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name__,
                                                                                            other=type(other).__name))

