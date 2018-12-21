import uuid
import warnings
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import TextIOBase
from ujson import loads, load, dumps

import chardet
from objectpath import Tree
from py._path.local import LocalPath

from hopla.documents.core import BUILT_INS
from hopla.documents.core import DEFAULT_ENCODING
from hopla.documents.core.document import BaseDocument
from hopla.documents.exceptions import CoreDocumentException, EncodingWarning, CircularReferenceWarning
from hopla.events import dispatcher
from hopla.events.signals import Signals
from hopla.logging import logger
from hopla.logging.log_exception import log_exception


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
    def ttl(self):
        return self._ttl

    @ttl.setter
    @log_exception(logger)
    def ttl(self, value):
        try:
            self._ttl = Decimal(value)
        except InvalidOperation:
            raise CoreDocumentException("ttl property should be a number!")

    @property
    def options(self):
        return self._options

    def validate(self, document):
        return True

    def get_data(self):
        return self._inner_data

    @property
    def create_date(self):
        return self._create_date

    @property
    def update_date(self):
        return self._update_date

    @log_exception(logger)
    def set_data(self, document):
        cached_value = None if self._new else self._inner_data
        if type(document) == str or type(document) == bytes:
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
            self._inner_data = document
        elif type(document) in BUILT_INS:
            self._inner_data = document
        elif type(document) == TextIOBase or type(document) == LocalPath:
            try:
                self._inner_data = load(document)
            except Exception as ex:
                raise CoreDocumentException(ex)
        else:
            self._inner_data = document

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
                        "to": self._inner_data
                    }},
                signal=Signals.DOCUMENT_UPDATED,
                sender=object())

    def __init__(self, *args, core_id=None, encoding=None, key=None, name=None, document=None, ttl=-1, options=None):
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
        self._inner_data = None
        self._ttl = ttl
        self._options = options
        self._new = True
        self._create_date = int(datetime.utcnow().timestamp())
        self._update_date = self._create_date

        if document is None:
            if len(args) == 1:
                self.set_data(args[0])
            elif len(args) > 1:
                self.set_data(args)
            else:
                self.set_data(None)
        else:
            self.set_data(document)

        dispatcher.send_message(
            message={
                "type": Signals.DOCUMENT_CREATED,
                "document": self},
            signal=Signals.DOCUMENT_CREATED,
            sender=object())
        self._new = False

    def __str__(self):
        return dumps(self.toDict(), **(dict(indent=4, sort_keys=True)))

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    @staticmethod
    def _to_dict(o):
        b_name = BaseDocument.__name__

        def dict_format(d):
            return {
                "__type": b_name,
                "__object": {
                    "__id": d.core_id,
                    "__name": d.name,
                    "__key": str(d.key) if d.key is not None else None,
                    "__encoding": d.encoding,
                    "__create_date": d.create_date,
                    "__update_date": d.update_date,
                    "__ttl": d.ttl,
                    "__data": Document._to_dict(d.get_data()),
                }
            }

        if type(o) == str:
            return o
        try:
            _ = iter(o)
            if issubclass(type(o), dict) or type(o) == dict:
                for k, v in o.items():
                    if issubclass(type(v), BaseDocument):
                        o[k] = dict_format(v)
                    else:
                        o[k] = Document._to_dict(v)
            elif issubclass(type(o), list) or type(o) == list:
                for idx, v in enumerate(o):
                    if issubclass(type(v), BaseDocument):
                        o[idx] = dict_format(v)
                    else:
                        o[idx] = Document._to_dict(v)
            return o
        except TypeError:
            if issubclass(type(o), BaseDocument):
                return dict_format(o)
            else:
                return o

    def toDict(self):
        return Document._to_dict(self)

    def clone(self, new=None):
        cloned = Document.from_str(dumps(self.toDict()), new=new)
        dispatcher.send_message(dict(type=Signals.DOCUMENT_CLONED, document=cloned, source=self),
                                Signals.DOCUMENT_CLONED)
        return cloned

    def children(self):
        tree = Tree(loads(str(self)))
        return [Document.from_str(dumps(d["__object"])) for d in
                list(tree.execute('$..*[@.__type is "BaseDocument" and @.__object]')) if
                d["__object"]["__id"] != self.core_id]

    @staticmethod
    def from_str(string_value, new=None):
        new_instance = new if type(new) == bool else False
        b_name = BaseDocument.__name__
        o = loads(string_value)

        if type(o) == dict and {"__type", "__object"} == set(o.keys()) and o["__type"] == b_name:
            return Document.from_str(dumps(o["__object"]), new=new_instance)

        if type(o) == dict and {"__id", "__name", "__key", "__encoding", "__create_date", "__update_date",
                                "__data", "__ttl"} == set(o.keys()):
            core_id = str(uuid.uuid4()) if new_instance else o["__id"]
            doc = Document(o["__data"], core_id=core_id,
                           encoding=o["__encoding"], key=o["__key"], name=o["__name"])

            if type(o["__data"]) == dict and {"__object", "__type"} == set(o["__data"].keys()) and \
                    o["__data"][
                        "__type"] == b_name:
                doc.set_data(Document.from_str(dumps(o["__data"]["__object"]), new=new_instance))
            else:
                doc.set_data(Document.from_str(dumps(o["__data"])))

            doc._create_date = int(datetime.utcnow().timestamp()) if new_instance else o["__create_date"]
            doc._update_date = doc._create_date if new_instance else o["__update_date"]
            doc._ttl = -1 if new_instance else o["__ttl"]

            return doc

        if type(o) == dict and {"__id", "__name", "__key", "__encoding", "__create_date", "__update_date",
                                "__data", "__ttl"} != set(o.keys()):
            return {k: Document.from_str(dumps(v), new=new_instance) for k, v in o.items()}

        if type(o) == list:
            return [Document.from_str(dumps(sub_o), new=new_instance) for sub_o in o]
        return o

    def __repr__(self):
        return "<class '{klass}' - value {value}>".format(klass=type(self).__name__, value=dumps(self.toDict()))

    def flatten_document(self):
        def _flatten_doc(o, dictionary):
            if issubclass(type(o), BaseDocument):
                o.set_data(_flatten_doc(o.get_data(), dictionary))

        doc = self.clone(new=False)
        dictionary = dict()
        _flatten_doc(doc, dictionary.get_data())

        return doc
