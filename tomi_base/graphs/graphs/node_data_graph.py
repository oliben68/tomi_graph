import ujson
from copy import deepcopy

from objectpath import Tree

from tomi_base.graphs.entity_class_generator import EntityClassGenerator
from tomi_base.graphs.graphs.graph import Graph
from tomi_base.graphs.indexes_support import IndexesSupport
from tomi_base.graphs.nodes.core.node import CoreNodeClass
from tomi_base.graphs.relationships.core.protection import Protection
from tomi_base.graphs.relationships.core.relation_type import RelationType
from tomi_base.graphs.relationships.relationship_class import RelationshipBaseClass
from tomi_base.graphs.version_aware_entity import VersionAwareEntity


class NodeDataGraph(Graph):
    NAMESPACE_DELIMITER = "::"

    def _flatten(self):

        def to_id(d):
            if issubclass(type(d), CoreNodeClass):
                return {
                    "__type": type(d).__name__,
                    "__id": d.core_id
                }
            return d

        def swap_with_id(d):
            if issubclass(type(d), dict) or type(d) == dict:
                for idx, val in d.items():
                    d[idx] = to_id(val)
                    swap_with_id(val)
            elif issubclass(type(d), list) or type(d) == list:
                for idx, val in enumerate(d):
                    d[idx] = to_id(val)
                    swap_with_id(val)
            elif issubclass(type(d), CoreNodeClass):
                self._nodes[d.core_id] = d
                d_data = d.get_data()
                if type(d_data) == tuple:
                    # some ugliness to bypass issues with the immutable nature of tuples
                    d.set_data(tuple(to_id(list(d_data))))
                else:
                    d.set_data(to_id(d_data))
                swap_with_id(d_data)

        swap_with_id([self.root_node] + self.root_node.children())

        for k, v in self._nodes.items():
            data = v.get_data()
            tree = Tree(ujson.loads(ujson.dumps(data)))
            if hasattr(tree, "data"):
                for ref in list(
                        tree.execute('$..*[@.__type and @.__id]')):
                    rel_type = EntityClassGenerator(RelationshipBaseClass, VersionAwareEntity, IndexesSupport).create(
                        self._rel_type)
                    self._relationships.append(rel_type(node_1=self._nodes[v.core_id], node_2=self._nodes[ref["__id"]],
                                                        rel_type=self._rel_type, protection=Protection.PRESERVE))

    def _assemble(self, entity):

        def to_doc(d):
            if (issubclass(type(d), dict) or type(d) == dict) and set(d.keys()) == {"__type", "__id"}:
                if d["__id"] not in self._nodes.keys():
                    # TODO: maybe raise exception here?
                    return d
                return self._nodes[d["__id"]]
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
            elif issubclass(type(d), CoreNodeClass):
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
    def id(self):
        return self._id

    @property
    def root_node(self):
        return self._root_node

    @root_node.setter
    def root_node(self, value):
        if not issubclass(type(value), CoreNodeClass):
            raise TypeError("Argument doc must be a class inheriting from {base}".format(base=CoreNodeClass.__name__))
        self._root_node = value
        self._relationships = []
        self._nodes = {}
        self._flatten()

    def assemble(self, update=None):
        root_id = self._root_node.core_id
        assembled_doc = self._assemble(deepcopy(self._nodes[root_id]))
        if update:
            self._root_node = assembled_doc
        return assembled_doc

    @property
    def root(self):
        return self._root_node.core_id

    @property
    def namespace_delimiter(self):
        return NodeDataGraph.NAMESPACE_DELIMITER

    @property
    def namespace_root(self):
        return self.root_node.core_id

    @property
    def graph(self):
        return self.toDict()

    @property
    def namespace_map(self):
        if self._namespace_map is None:
            self._namespace_map = {self.root: self.root}

            def calculate_namespace(parent_namespace):
                core_id = parent_namespace.split(self.namespace_delimiter)[-1]
                for rel in [r for r in self._relationships if r.node_1.core_id == core_id]:
                    child_namespace = "{base}{delimiter}{entity_id}".format(base=parent_namespace,
                                                                            entity_id=rel.node_2.core_id,
                                                                            delimiter=self.namespace_delimiter)
                    self._namespace_map[rel.node_2.core_id] = child_namespace
                    calculate_namespace(child_namespace)

            calculate_namespace(self.root)
        return self._namespace_map

    @property
    def isolates(self):
        return []

    def __init__(self, doc, rel_type=None, do_not_clone=None):
        """

        :param doc:
        :param rel_type:
        :param do_not_clone:
        """
        super().__init__(namespace_root=NodeDataGraph.NAMESPACE_DELIMITER)
        if not issubclass(type(doc), CoreNodeClass):
            raise TypeError("Argument doc must be a class inheriting from {base}".format(base=CoreNodeClass.__name__))

        self._root_node = doc if do_not_clone else deepcopy(doc)
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

    @staticmethod
    def erase(self, obj):
        pass

    def clear(self):
        pass
