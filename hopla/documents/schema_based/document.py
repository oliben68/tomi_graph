from jsonschema import validate, ValidationError

import warnings
from hopla.documents.exceptions import SchemaValidationException, SchemaValidationWarning
from hopla.documents.document import Document
from hopla.logging import logger
from hopla.logging.log_exception import log_exception
from hopla.events.signals import Signals
from hopla.events import dispatcher


class ValidatedDocument(Document):
    def __init__(self, *args, core_id=None, encoding=None, key=None, name=None, document=None, ttl=-1, options=None):
        """

        :param args:
        :param core_id:
        :param encoding:
        :param key:
        :param name:
        :param document:
        :param options:
            options = {
                "schema": {
                    "value": <schema dictionary>    # Schema definition
                    "as_warning": True|False        # Treats validation errors as warnings
                }
            }
        """
        super().__init__(*args, core_id=core_id, encoding=encoding, key=key, name=name, document=document, ttl=ttl,
                         options=options)

    @log_exception(logger)
    def validate(self, document):
        schema = self.options["schema"]
        info = None
        if type(schema["data"]) == dict:
            try:
                validate(document, schema["data"])
                info = Document(schema["data"])
            except ValidationError as ex:
                if "as_warning" in schema and schema["as_warning"]:
                    warnings.warn(SchemaValidationWarning(ex))
                else:
                    raise SchemaValidationException(ex)
        return dict(valid=True, info=info)

    @log_exception(logger)
    def set_data(self, document):
        if "schema" in self.options.keys() and type(self.options["schema"]) == dict and "value" in self.options[
            "schema"].keys():
            validation = self.validate(document)
            if validation["valid"]:
                dispatcher.send_message(message={
                    "type": Signals.DOCUMENT_VALIDATED,
                    "document": self,
                    "validator": validation["info"]},
                    signal=Signals.DOCUMENT_VALIDATED,
                    sender=object())
                super().set_data(document)
            else:
                raise SchemaValidationException("Error validating document: {info}".format(info=validation["info"]))
        else:
            warnings.warn(SchemaValidationWarning("Missing validator"))
            super().set_data(document)
