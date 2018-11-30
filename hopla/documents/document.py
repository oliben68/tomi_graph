import uuid
import warnings
from io import TextIOBase
from ujson import loads, load, dumps

import chardet
from py._path.local import LocalPath

from hopla.documents.core import DEFAULT_ENCODING
from hopla.documents.core import BUILT_INS
from hopla.documents.core.document import BaseDocument
from hopla.documents.exceptions import CoreDocumentException, EncodingWarning, CircularReferenceWarning
from hopla.logging import logger
from hopla.logging.log_exception import log_exception
from hopla.events.signals import Signals
from hopla.events import dispatcher
from datetime import datetime


class Document(BaseDocument):
    @property
    def core_id(self):
        return self._core_id

    @property
    def key(self):
        return self._key

    @property
    def encoding(self):
        return self._encoding

    @property
    def name(self):
        return self._name

    @name.setter
    @log_exception(logger)
    def name(self, value):
        if type(value) == str:
            self._name = value
        else:
            raise CoreDocumentException("name property is of type str!")

    @property
    def options(self):
        return self._options

    def validate(self, document):
        return True

    def get_document(self):
        return self._inner_value

    @property
    def create_date(self):
        return self._create_date

    @property
    def update_date(self):
        return self._update_date

    @log_exception(logger)
    def set_document(self, document):
        cached_value = None if self._new else self._inner_value
        if type(document) == str or type(document) == bytes:
            try:
                if type(document) == bytes:
                    encoding = chardet.detect(document)["encoding"]
                    if chardet.detect(document)["encoding"].lower() != self._encoding.lower():
                        warnings.warn(
                            EncodingWarning("Detected encoding {d} is different from document encoding {e}.".format(
                                d=encoding, e=self._encoding)))
                        self._encoding = encoding.lower()
                        document = document.decode(encoding)
                    else:
                        document = document.decode(self._encoding)
                self._inner_value = document
            except Exception as ex:
                raise CoreDocumentException(ex)
        elif type(document) in BUILT_INS:
            self._inner_value = document
        elif type(document) == TextIOBase or type(document) == LocalPath:
            try:
                self._inner_value = load(document)
            except Exception as ex:
                raise CoreDocumentException(ex)
        else:
            self._inner_value = document

        try:
            _ = str(self)
        except RecursionError:
            warnings.warn(CircularReferenceWarning("Circular reference detected."))

        if not self._new:
            self._update_date = datetime.utcnow()

            dispatcher.send_message(
                message={
                    "type": Signals.DOCUMENT_UPDATED,
                    "document": self,
                    "changes": {
                        "from": cached_value,
                        "to": self._inner_value
                    }},
                signal=Signals.DOCUMENT_UPDATED,
                sender=object())

    def __init__(self, *args, core_id=None, encoding=None, key=None, name=None, document=None, options=None):
        """

        :param args:
        :param core_id:
        :param encoding:
        :param key:
        :param name:
        :param document:
        :param options:
        """
        self._core_id = str(uuid.uuid4()) if core_id is None else str(core_id)
        self._encoding = DEFAULT_ENCODING if type(encoding) != str else encoding
        self._key = key
        self._name = name
        self._inner_value = None
        self._options = options
        self._new = True
        self._create_date = datetime.utcnow()
        self._update_date = self._create_date

        if document is None:
            if len(args) == 1:
                self.set_document(args[0])
            elif len(args) > 1:
                self.set_document(args)
            else:
                self.set_document(None)
        else:
            self.set_document(document)

        dispatcher.send_message(
            message={
                "type": Signals.DOCUMENT_CREATED,
                "document": self},
            signal=Signals.DOCUMENT_CREATED,
            sender=object())
        self._new = False

    def clone(self, new=None):
        cloned = Document.from_str(str(self), new=True)
        if type(new) == bool or False:
            cloned._core_id = self.core_id
        dispatcher.send_message(dict(type=Signals.DOCUMENT_CLONED, document=cloned, source=self),
                                Signals.DOCUMENT_CLONED)
        return cloned

    def __str__(self):
        return dumps(self.toDict(), **(dict(indent=4, sort_keys=True)))

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def toDict(self):
        o = self.get_document()
        b_name = BaseDocument.__name__
        if issubclass(type(o), BaseDocument):
            doc = {"__type": b_name, "__object": o.toDict()}
        elif type(o) in BUILT_INS or any([issubclass(type(o), i) for i in BUILT_INS]):
            if issubclass(type(o), list) or type(o) == list:
                doc = [
                    (i if not issubclass(type(i), BaseDocument) else {"__type": b_name, "__object": i.toDict()})
                    for i in o]
            elif issubclass(type(o), dict) or type(o) == dict:
                doc = {k: (v if not issubclass(type(v), BaseDocument) else {"__type": b_name, "__object": v.toDict()})
                for k, v in o.items()}
            else:
                doc = o
        else:
            # noinspection PyBroadException
            try:
                doc = loads(dumps(self.get_document()))
            except Exception:
                doc = o

        return {
            "__id": self.core_id,
            "__name": self._name,
            "__key": str(self.key) if self.key is not None else None,
            "__encoding": self.encoding,
            "__create_date": self.create_date,
            "__update_date": self.update_date,
            "__document": doc,
        }

    @staticmethod
    def from_str(string_value, new=None):
        o = loads(string_value)
        if type(o) == dict and {"__id", "__name", "__key", "__encoding", "__create_date", "__update_date",
                                "__document"} == set(o.keys()):
            if type(o["__document"]) == dict and {"__object", "__type"} == set(o["__document"].keys()) and \
                    o["__document"][
                        "__type"] == BaseDocument.__name__:
                sub_o = Document.from_str(dumps(o["__document"]["__object"]), new=new)
                o["__document"] = sub_o
            doc = Document(o["__document"], core_id=o["__id"] if new is None or not new else str(uuid.uuid4()),
                           encoding=o["__encoding"], key=o["__key"], name=o["__name"])
            doc._create_date = o["__create_date"]
            doc._update_date = o["__update_date"]
            return doc
        if type(o) == list:
            return [Document.from_str(sub_o, new=new) for sub_o in o]
        return o

    def __repr__(self):
        return "<class '{klass}' - value {value}>".format(klass=type(self).__name__, value=dumps(self.toDict()))
