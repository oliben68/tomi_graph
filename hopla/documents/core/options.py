from hopla.documents.core.properties import Properties
from hopla.documents.core.schema import Schema, NOTHING_SCHEMA

import attr


@attr.s
class Options(Properties):
    schema = attr.ib(default=NOTHING_SCHEMA, type=Schema)

    @schema.validator
    def _schema(self, attributes, value):
        if type(value) != attributes.type and value is not None:
            raise TypeError(
                "{name} needs to be of type {klass}.".format(name=attributes.name, klass=attributes.type.__name__))
        if value is None or value.value == NOTHING_SCHEMA.value:
            self.schema = None

    @staticmethod
    def from_dict(value):
        if type(value) != dict:
            raise TypeError(
                "{name} needs to be of class {klass}.".format(name="value", klass=dict))
        return Options(schema=Schema.from_dict(value))
