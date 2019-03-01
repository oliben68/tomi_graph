from abc import ABC, abstractmethod


class GraphEntityClassGenerator(ABC):
    @staticmethod
    @abstractmethod
    def create(entity_type=None, indexes=None):
        raise NotImplementedError
