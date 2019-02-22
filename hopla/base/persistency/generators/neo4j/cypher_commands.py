from abc import abstractmethod

from hopla.base.persistency.generators.base_generator import BaseGenerator
from hopla.base.persistency.generators.neo4j import BooleanOperator


class CypherCommands(BaseGenerator):
    excluded_properties = []
    property_prefix = ""

    @staticmethod
    @abstractmethod
    def generate_create(variable=None, entity_type=None, **properties):
        raise NotImplementedError

    @abstractmethod
    def self_generate_create(self, variable=None):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def generate_merge(variable=None, entity_type=None, **properties):
        raise NotImplementedError

    @abstractmethod
    def self_generate_merge(self, variable=None):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def generate_match(node, variable=None):
        raise NotImplementedError

    @abstractmethod
    def self_generate_match(self, variable=None):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def generate_where(boolean_operator=None, excluded=None, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def self_generate_where(self, boolean_operator=None, excluded=None):
        raise NotImplementedError

    # @abstractmethod
    # def DELETE(self):
    #     raise NotImplementedError
    #
    # @abstractmethod
    # def REMOVE(self):
    #     raise NotImplementedError
    #
    # @abstractmethode
    # def SET(self):
    #     raise NotImplementedError

    @staticmethod
    def properties_values_map(excluded=None, property_prefix=None, **properties):
        if len(properties) == 0:
            return "{}"

        property_prefix = "" if type(property_prefix) != str else property_prefix
        excluded_properties = [] if excluded is None else [property_prefix + e for e in excluded] + excluded
        keys_values = [
            "`{key}`: {value}".format(key=key.replace(property_prefix, ""), value=CypherCommands.format_value(value))
            for key, value in properties.items() if key not in excluded_properties and value is not None
            ]
        return "{{{props}}}".format(props=", ".join(keys_values))

    @staticmethod
    def properties_values_list(boolean_operator=None, excluded=None, **properties):
        if len(properties) == 0:
            return ""

        if type(boolean_operator) != BooleanOperator:
            boolean_operator = BooleanOperator.AND

        properties_values = [
            "`{k}` = {v}".format(k=key.replace(CypherCommands.property_prefix, ""),
                                 v=CypherCommands.format_value(value)) for key, value in properties.items() if
            key not in (CypherCommands.excluded_properties if excluded is None else excluded) and value is not None
        ]
        return boolean_operator.value.join(properties_values)

