from hopla.documents.core.properties import Properties, NOTHING_DICT
import attr


@attr.s
class Schema(Properties):
    # value property
    value = attr.ib(default=NOTHING_DICT, type=dict)

    @value.validator
    def _value(self, attributes, value):
        if value == NOTHING_DICT:
            raise ValueError(
                "{name} is a mandatory field and needs to be pass to the constructor.".format(name=attributes.name))
        if type(value) != attributes.type:
            raise TypeError(
                "{name} needs to be of type {klass}.".format(name=attributes.name, klass=attributes.type.__name__))

    @staticmethod
    def from_dict(value):
        if type(value) != dict:
            raise TypeError(
                "{name} needs to be of type {klass}.".format(name="value", klass=dict.__name__))
        if "value" in value.keys():
            return Schema(value=value["value"])
        return Schema(value=value)


# Placeholder
NOTHING_SCHEMA = Schema(value=dict(value=NOTHING_DICT))
