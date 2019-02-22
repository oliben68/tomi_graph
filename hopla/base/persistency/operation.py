from datetime import datetime
from enum import Enum
from ujson import dumps


class OperationType(Enum):
    INIT = "Initialisation"
    CREATE = "Create"
    DELETE = "Delete"
    RETRIEVE = "Retrieve"
    UNKNOWN = "Unknown"
    NONE = "None"


class Operation(object):
    @property
    def operation(self):
        return self._operation

    @property
    def command(self):
        return self._command

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

    @staticmethod
    def create(operation, commands=None, data=None, comment=None, timestamp=None):
        if type(commands) == str or commands is None:
            return [Operation(operation, command=commands, data=data, comment=comment, timestamp=timestamp)]
        try:
            iter(commands)
            operations = []
            for command in commands:
                operations.append(Operation(operation, command=command, data=data, comment=comment))
            return operations
        except TypeError:
            return [Operation(operation, command=commands, data=data, comment=comment, timestamp=timestamp)]

    def failed(self):
        return isinstance(self._data, Exception)

    def __init__(self, operation, command=None, data=None, comment=None, timestamp=None):
        self._operation = OperationType.UNKNOWN if type(operation) != OperationType else operation
        self._data = data
        self._command = command
        self._comment = "" if comment is None else str(comment)
        try:
            self._timestamp = datetime.utcnow().timestamp() if timestamp is None else float(timestamp)
        except ValueError:
            self._timestamp = datetime.utcnow().timestamp()

    def __str__(self):
        return dumps(dict(operation=self.operation.value, comment=self.comment, timestamp=self.timestamp))

    def __hash__(self):
        return hash(str(self))
