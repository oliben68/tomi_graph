from datetime import datetime
from enum import Enum
from ujson import dumps


class Operations(Enum):
    INIT = "Initialisation"
    UNKNOWN = "Unknown"
    NONE = "None"


class Operation(object):
    @property
    def operation(self):
        return self._operation

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def comment(self):
        return self._comment

    @property
    def timestamp(self):
        return self._timestamp

    def failed(self):
        return isinstance(self._data, Exception)

    def __init__(self, operation, data=None, comment=None, timestamp=None):
        self._operation = Operations.UNKNOWN if type(operation) != Operations else operation
        self._data = data
        self._comment = "" if comment is None else str(comment)
        try:
            self._timestamp = datetime.utcnow().timestamp() if timestamp is None else float(timestamp)
        except ValueError:
            self._timestamp = datetime.utcnow().timestamp()

    def __str__(self):
        return dumps(dict(operation=self.operation.value, comment=self.comment, timestamp=self.timestamp))

    def __hash__(self):
        return hash(str(self))
