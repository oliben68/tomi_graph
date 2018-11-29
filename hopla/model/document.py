from abc import ABC

from hopla.documents.schema_based.document import ValidatedDocument
from hopla.model.core.document import ModelDocument


class Document(ValidatedDocument, ModelDocument, ABC):
    def __init__(self, *args, core_id=None, encoding=None, key=None, name=None, document=None, options=None):
        super().__init__(*args, core_id=core_id, encoding=encoding, key=key, name=name, document=document,
                         options=options)

    def save(self):
        pass

    def read(self):
        pass

    def delete(self):
        pass
