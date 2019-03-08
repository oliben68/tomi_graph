from abc import abstractmethod
from ujson import dumps

from tomi_graph.base_graph_entity import BaseGraphEntity
from tomi_graph.entity_category import EntityCategory


class CoreIndex(BaseGraphEntity):
    category = EntityCategory.INDEX

    @property
    @abstractmethod
    def node_type(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def field(self):
        raise NotImplementedError

    @staticmethod
    def serialize_to_string(d):
        return dumps(d, **(dict(indent=4, sort_keys=True)))

    @abstractmethod
    def __init__(self, node_type, field):
        raise NotImplementedError
