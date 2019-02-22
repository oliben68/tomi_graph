from abc import ABC

from hopla_graph.shared.tools import Tools


class BaseGenerator(ABC):
    entity_type = type(None)
    tools = Tools()

    @property
    def entity(self):
        return self._entity

    def __init__(self, entity):
        if type(entity) != self.entity_type and not isinstance(entity, self.entity_type):
            raise TypeError(
                "Wrong root_node type: should be {type} but is {wrong_type}.".format(type=self.entity_type.__name,
                                                                                  wrong_type=type(entity).__name))
        self._entity = entity

    @staticmethod
    def format_value(value):
        return value if BaseGenerator.tools.is_numeric(value) else '"' + str(value) + '"'
