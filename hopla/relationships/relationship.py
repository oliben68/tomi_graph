import inspect
import weakref
from enum import Enum
from uuid import uuid4

from hopla.entities.core.entity import BaseEntity
from hopla.relationships.core import Direction, Protection, RelationType, NULL_VALUE
from hopla.relationships.core.relationship import BaseRelationship
from hopla.relationships.finalizers import self_reset_finalizer, preserve_entity_finalizer


class Relationship(BaseRelationship):
    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    @property
    def rel_type(self):
        return self._rel_type

    def return_entity_value(self, attribute_name):
        if getattr(self, attribute_name, None) is None:
            return None
        entity = getattr(self, attribute_name, None)()
        if entity is None:
            if attribute_name[1:] in self._safe.keys():
                return self._safe[attribute_name[1:]]
            return None
        return entity

    @property
    def entity_1(self):
        if self._entity_1 is None:
            return None
        return self._entity_1()

    @property
    def entity_2(self):
        if self._entity_2 is None:
            return None
        return self._entity_2()

    @property
    def direction(self):
        return self._direction

    @property
    def protection(self):
        return self._protection

    @property
    def safe(self):
        return self._safe

    @property
    def on_gc_collect(self):
        return self._on_gc_collect

    def wire_protection(self):
        self._refs.clear()
        # on_gc_collect has predominance over protection
        if callable(self.on_gc_collect) and {'args', 'kwargs'}.issubset(
                set(inspect.getcallargs(self.on_gc_collect).keys())):
            self._refs['entity_1'] = weakref.finalize(self.entity_1, self.on_gc_collect, relationship=self)
            self._refs['entity_2'] = weakref.finalize(self.entity_2, self.on_gc_collect, relationship=self)
        else:
            if self._protection == Protection.CASCADE_DELETE:
                self._refs['entity_1'] = weakref.finalize(self.entity_1, self_reset_finalizer, relationship=self)
                self._refs['entity_2'] = weakref.finalize(self.entity_2, self_reset_finalizer, relationship=self)
            elif self._protection == Protection.PRESERVE:
                self._refs['entity_1'] = weakref.finalize(self.entity_1, preserve_entity_finalizer,
                                                          relationship=self, safe=self._safe, property="entity_1",
                                                          value=self.entity_1.toDict())
                self._refs['entity_2'] = weakref.finalize(self.entity_2, preserve_entity_finalizer,
                                                          relationship=self, safe=self._safe, property="entity_2",
                                                          value=self.entity_2.toDict())

    def __init__(self, entity_1, entity_2, rel_type=None, direction=None, protection=None, on_gc_collect=None,
                 **kwargs):
        self._id = str(uuid4())

        self._entity_1 = weakref.ref(entity_1)
        self._entity_2 = weakref.ref(entity_2)

        self._protection = protection if type(protection) == Protection else Protection.NONE
        self._on_gc_collect = on_gc_collect
        self._refs = {}
        self._safe = {}
        self.wire_protection()

        self._rel_type = Relationship.__name__.upper() if rel_type is None or type(
            rel_type) != str else rel_type.upper()
        self._direction = direction if type(direction) == Direction else Direction.NONE
        self._data = kwargs

    def toDict(self):
        def value(v):
            if issubclass(type(v), Enum):
                return v.name
            elif type(v) == weakref.ReferenceType:
                entity = v()
                return entity if issubclass(type(entity), BaseEntity) else None
            else:
                return v

        return {"_" + k: value(v) for k, v in self.__dict__.items()}

    def __repr__(self):
        return repr(self.toDict())

    def __str__(self):
        return str(self.toDict())

    def __call__(self, rel_type=None, protection=None, data=None, on_gc_collect=NULL_VALUE):
        if on_gc_collect != NULL_VALUE:
            self._on_gc_collect = on_gc_collect
        self._rel_type = self._rel_type if rel_type is None or type(rel_type) not in [
            str, RelationType] else rel_type.upper()
        if self._protection != protection:
            self._protection = protection if type(protection) == Protection else self._protection
            self.wire_protection()
        self._data = data if data is None else data

        return self

    def __reset__(self):
        self._id = None
        self._entity_1 = None
        self._entity_2 = None
        self._safe = {}
        self._direction = Direction.NONE
        self(rel_type=RelationType.NONE, protection=Protection.NONE, data={}, on_gc_collect=None)

    def __add__(self, other):
        return Relationship(self.entity_2, other.entity_1)
