from abc import ABC, abstractmethod

from tomi_base.base.graphs.entity_category import EntityCategory


class BaseGraphEntity(ABC):
    category = EntityCategory.CORE

    @abstractmethod
    def to_graph(self):
        raise NotImplementedError