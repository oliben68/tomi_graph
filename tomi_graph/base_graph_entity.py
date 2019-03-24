from abc import ABC, abstractmethod

from tomi_graph.entity_category import EntityCategory


class GraphEntity(ABC):
    category = EntityCategory.CORE

    @abstractmethod
    def to_graph(self):
        raise NotImplementedError
