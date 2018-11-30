from hopla.documents.core import DEFAULT_ENCODING
from hopla.documents.schema_based.document import ValidatedDocument


class Results(ValidatedDocument):
    def __init__(self):
        options = {"schema": {
            "value": {
                "type": "object",
                "properties": {
                    "results": {"type": "object"},
                    "time": {"type": "float"},
                }
            }}}

        super().__init__(encoding=DEFAULT_ENCODING, options=options)
