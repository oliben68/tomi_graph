import ujson
from copy import deepcopy
from ujson import loads

from objectpath import Tree

from hopla.entities.core.entity import BaseEntity
from hopla.relationships.core import RelationType, Protection
from hopla.relationships.relationship import Relationship

NAMESPACE_DELIMITER = "::"


class Graph(object):
    def _flatten(self):

        def to_id(d):
            if issubclass(type(d), BaseEntity):
                return {
                    "__type": d.entity_type,
                    "__id": d.core_id
                }
            return d

        def swap_with_id(d):
            if issubclass(type(d), dict) or type(d) == dict:
                for idx, v in d.items():
                    d[idx] = to_id(v)
                    swap_with_id(v)
            elif issubclass(type(d), list) or type(d) == list:
                for idx, v in enumerate(d):
                    d[idx] = to_id(v)
                    swap_with_id(v)
            elif issubclass(type(d), BaseEntity):
                self._entities_refs[d.core_id] = d
                d_data = d.get_data()
                if type(d_data) == tuple:
                    # some ugliness to bypass issues with the immutable nature of tuples
                    d.set_data(tuple(to_id(list(d_data))))
                else:
                    d.set_data(to_id(d_data))
                swap_with_id(d_data)

        swap_with_id([self.entity] + self.entity.children())

        for k, v in self._entities_refs.items():
            data = v.get_data()
            tree = Tree(ujson.loads(ujson.dumps(data)))
            if hasattr(tree, "data"):
                for ref in list(
                        tree.execute('$..*[@.__type and @.__id]')):
                    self._relationships.append(Relationship(
                        entity_1=self._entities_refs[v.core_id],
                        entity_2=self._entities_refs[ref["__id"]],
                        rel_type=self._rel_type,
                        protection=Protection.PRESERVE))

    def _refs(self, core_id):
        tree = Tree(loads(str(self._entities_refs[core_id])))
        return list(tree.execute('$..*[@.__type is "BaseEntity" and @.__id]'))

    def _assemble(self, entity):

        def to_doc(d):
            if (issubclass(type(d), dict) or type(d) == dict) and set(d.keys()) == {"__type", "__id"}:
                if d["__id"] not in self._entities_refs.keys():
                    # TODO: maybe raise exception here?
                    return d
                return self._entities_refs[d["__id"]]
            return d

        def swap_with_doc(d):
            if issubclass(type(d), dict) or type(d) == dict:
                if set(d.keys()) == {"__type", "__id"}:
                    return swap_with_doc(to_doc(d))
                else:
                    for idx, v in d.items():
                        d[idx] = swap_with_doc(to_doc(v))
            elif issubclass(type(d), list) or type(d) == list:
                for idx, v in enumerate(d):
                    d[idx] = swap_with_doc(to_doc(v))
            elif issubclass(type(d), BaseEntity):
                d_data = d.get_data()
                if type(d_data) == tuple:
                    # some ugliness to bypass issues with the immutable nature of tuples
                    d.set_data(tuple(swap_with_doc(list(d_data))))
                else:
                    d.bypass_update_date()
                    d.set_data(swap_with_doc(d_data))
            return d

        ret = swap_with_doc(entity)
        return ret

    @property
    def entity(self):
        return self._doc

    @entity.setter
    def entity(self, value):
        if not issubclass(type(value), BaseEntity):
            raise TypeError("Argument doc must be a class inheriting from {base}".format(base=BaseEntity.__name__))
        self._doc = value
        self._relationships = []
        self._entities_refs = {}
        self._flatten()

    def assemble(self, update=None):
        root_id = self._doc.core_id
        assembled_doc = self._assemble(deepcopy(self._entities_refs[root_id]))
        if update:
            self.entity = assembled_doc
        return assembled_doc

    @property
    def root(self):
        return self._doc.core_id

    @property
    def entities_refs(self):
        return self._entities_refs

    @entities_refs.setter
    def entities_refs(self, value):
        if issubclass(type(value), list) and type(value) == list:
            if not all([issubclass(type(d), BaseEntity) for d in value]):
                raise TypeError(
                    "The entities_refs property should be a list where all element are of type {doc}.".format(
                        doc=BaseEntity.__name__))
            self._entities_refs = BaseEntity.serialize_to_string(value)

        raise TypeError("The entities_refs property should be a list of {doc}.".format(doc=BaseEntity.__name__))

    @property
    def relationships(self):
        return self._relationships

    @property
    def namespace_map(self):
        if self._namespace_map is None:
            self._namespace_map = {self.root: self.root}

            def calculate_namespace(parent_namespace):
                core_id = parent_namespace.split(NAMESPACE_DELIMITER)[-1]
                for rel in [r for r in self._relationships if r.entity_1.core_id == core_id]:
                    child_namespace = "{base}{delimitor}{entity_id}".format(base=parent_namespace,
                                                                            entity_id=rel.entity_2.core_id,
                                                                            delimitor=NAMESPACE_DELIMITER)
                    self._namespace_map[rel.entity_2.core_id] = child_namespace
                    calculate_namespace(child_namespace)

            calculate_namespace(self.root)
        return self._namespace_map

    @property
    def graph(self):
        return self.toDict()

    def __init__(self, doc, rel_type=None, do_not_clone=None):
        """

        :param doc:
        :param rel_type:
        :param do_not_clone:
        """
        if not issubclass(type(doc), BaseEntity):
            raise TypeError("Argument doc must be a class inheriting from {base}".format(base=BaseEntity.__name__))
        self._doc = doc if do_not_clone else deepcopy(doc)
        self._relationships = []
        self._entities_refs = {}
        self._namespace_map = None

        if rel_type is None or type(rel_type) not in (str, RelationType):
            self._rel_type = RelationType.EMBEDDED.string
        else:
            self._rel_type = rel_type.string if type(rel_type) == RelationType else rel_type.upper()

        self._flatten()

    def __repr__(self):
        return repr(self.toDict())

    def __str__(self):
        return str(self.toDict())

    def toDict(self):
        return dict(__entities={k: v.toDict() for k, v in self._entities_refs.items()},
                    __relationships=self.relationships,
                    __namespace_map=self.namespace_map)
