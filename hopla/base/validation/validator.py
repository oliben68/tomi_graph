import warnings

from hopla.base.events import dispatcher
from hopla.base.events.signals import Signals
from jsonschema import validate, ValidationError

from hopla.base.graphs.nodes.exceptions import SchemaValidationException, SchemaValidationWarning
from hopla.base.validation.core.validator import BaseValidator


class Validator(BaseValidator):
    @property
    def validation_expression(self):
        return self._validation_expression

    def __init__(self, validation_expression):
        if type(validation_expression) != dict or not issubclass(type(validation_expression), dict):
            raise TypeError("The validation expression needs to be a dictionary or a compatible type.")
        self._validation_expression = validation_expression

    def validate(self, data):
        valid = False
        info = None
        validation_exception = None
        if type(self._validation_expression["data"]) == dict:
            try:
                validate(data, self._validation_expression["data"])
                info = self._validation_expression["data"]
            except ValidationError as ex:
                validation_exception = ex
                if "as_warning" in self._validation_expression and self._validation_expression["as_warning"]:
                    warnings.warn(SchemaValidationWarning(ex))
                else:
                    raise SchemaValidationException(ex)
            valid = True

        if valid:
            dispatcher.send_message(message={
                "type": Signals.ENTITY_VALIDATED,
                "node": self,
                "validator": info},
                signal=Signals.ENTITY_VALIDATED,
                sender=object())
        else:
            raise SchemaValidationException(
                "Failed validation. Details: {details}.".format(details=validation_exception))

        return valid
