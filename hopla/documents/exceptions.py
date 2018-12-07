class CoreDocumentException(Exception):
    pass


class CircularDocumentException(Exception):
    pass


class SchemaValidationException(Exception):
    pass


class CircularReferenceWarning(Warning):
    pass


class EncodingWarning(Warning):
    pass


class SchemaValidationWarning(Warning):
    pass


class SchemaDataException(Exception):
    pass
