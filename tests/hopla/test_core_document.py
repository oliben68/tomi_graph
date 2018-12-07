import warnings
from ujson import dumps
from uuid import uuid4

import pytest
from pydispatch import dispatcher
from testfixtures import LogCapture

from hopla.documents.core import DEFAULT_ENCODING
from hopla.documents.core.options import Options
from hopla.documents.core.properties import Properties
from hopla.documents.core.schema import Schema
from hopla.documents.document import Document
from hopla.documents.exceptions import CoreDocumentException, EncodingWarning, CircularReferenceWarning, \
    SchemaValidationWarning, SchemaValidationException
from hopla.documents.schema_based.document import ValidatedDocument
from hopla.events.dispatcher import connect_handler, disconnect_handler
from hopla.events.exceptions import HandlerArgsCountException
from hopla.events.signals import Signals
from hopla.logging import create_logger
from hopla.logging.log_exception import log_exception

globals()["cache"] = {}

TEST_VAL = {"document": {"test": "value"}}
TEST_DOCUMENT = "THIS IS A TEST"


@pytest.fixture(autouse=True)
def capture_logs():
    with LogCapture() as capture:
        yield capture


def test_init():
    doc = Document()
    assert doc.get_document() is None
    assert doc.core_id is not None
    assert type(doc.core_id) == str
    assert doc.key is None
    assert doc.encoding == "utf-8"

    core_id = str(uuid4())
    key = "this is a key"
    doc = Document(core_id=core_id, key=key, document=TEST_VAL)
    assert doc.core_id == core_id
    assert doc.key == key
    assert doc.get_document() == TEST_VAL

    doc = Document(document=TEST_DOCUMENT)
    assert doc.get_document() == TEST_DOCUMENT

    encoding = DEFAULT_ENCODING
    bytes_val = TEST_DOCUMENT.encode(encoding)
    doc = Document(document=TEST_DOCUMENT)
    assert doc.get_document() == bytes_val.decode(encoding)

    encoding = "utf-16"
    bytes_val = TEST_DOCUMENT.encode(encoding)
    doc = Document(document=bytes_val, encoding=encoding)
    assert doc.get_document() == bytes_val.decode(encoding)


def test_name_is_string():
    with pytest.raises(Exception) as e_info:
        Document(name=123)
        assert type(e_info) == CoreDocumentException
    Document(name="name")
    assert True


def test_core_validate():
    assert Document().validate(None)


def test_ttl_is_numeric():
    with pytest.raises(Exception) as e_info:
        Document(ttl="NOPE")
        assert type(e_info) == CoreDocumentException
    Document(ttl=0)
    Document(ttl="0")
    Document(ttl="0.123")
    Document(ttl=.123)


def test_encoding_warning(recwarn):
    encoding = "utf-16"
    bytes_val = dumps(TEST_VAL).encode(encoding)
    warnings.simplefilter("always")
    doc = Document(document=bytes_val)
    assert len(recwarn) == 1
    assert recwarn.pop(EncodingWarning)
    assert doc.encoding.lower() == encoding


def test_circular_warning(recwarn):
    warnings.simplefilter("always")
    inner_doc = Document()
    main_doc = Document(document=inner_doc)
    inner_doc.set_document(main_doc)
    assert len(recwarn) == 1
    assert recwarn.pop(CircularReferenceWarning)


def test_init_with_serialize_exc():
    val = dumps({"test": "value"})
    with pytest.raises(Exception) as e_info:
        Document(document=val[0:len(val) - 2])
        assert type(e_info) == CoreDocumentException
        assert "Unexpected character" in str(e_info)


def test_init_stream(tmpdir):
    str_value = dumps(TEST_VAL)
    val = tmpdir.mkdir("sub").join("value.json")
    val.write(str_value)
    doc = Document(document=val)
    assert doc.get_document() == TEST_VAL


def test_init_stream_with_exc(tmpdir):
    str_value = dumps(TEST_VAL)
    val = tmpdir.mkdir("sub").join("value.json")
    val.write(str_value[0:len(str_value) - 2])
    with pytest.raises(Exception) as e_info:
        Document(document=val)
        assert type(e_info) == CoreDocumentException
        assert "Unexpected character" in str(e_info)


def test_schema_validated_document():
    options = {"schema": {
        "value": {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "name": {"type": "string"},
            }
        }}}
    value_doc = {"name": "Lord of the ring", "price": 34.99}
    validated_doc = ValidatedDocument(value_doc, options=options)
    assert validated_doc.get_document() == value_doc


def test_schema_validated_document_exception():
    options = {"schema": {
        "value": {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "__name": {"type": "string"},
            }
        }}}
    with pytest.raises(Exception) as e_info:
        ValidatedDocument({"__name": "Lord of the ring", "price": "34.99"}, options=options)
        assert type(e_info) == SchemaValidationException

    options = {"schema": {
        "value": {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "__name": {"type": "string"},
            }
        },
        "as_warning": False}}

    with pytest.raises(Exception) as e_info:
        ValidatedDocument({"__name": "Lord of the ring", "price": "34.99"}, options=options)
        assert type(e_info) == SchemaValidationException


def test_schema_validated_document_warning(recwarn):
    options = {"schema": {
        "value": {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "__name": {"type": "string"},
            }
        },
        "as_warning": True}}
    warnings.simplefilter("always")
    ValidatedDocument({"__name": "Lord of the ring", "price": "34.99"}, options=options)
    assert len(recwarn) == 1
    assert recwarn.pop(SchemaValidationWarning)


def test_disconnect_event_signal():
    def handle_creation(_):
        assert False

    connect_handler(handle_creation, signal=Signals.DOCUMENT_CREATED, sender=dispatcher.Any)
    disconnect_handler(signal=Signals.DOCUMENT_CREATED)
    _ = Document(TEST_DOCUMENT)
    assert True


def test_disconnect_event_handler():
    def handle_creation(_):
        assert False

    connect_handler(handle_creation, signal=Signals.DOCUMENT_CREATED, sender=dispatcher.Any)
    disconnect_handler(handler=handle_creation)
    _ = Document(TEST_DOCUMENT)
    assert True


def test_disconnect_event_handler_and_signal():
    def handle_creation(_):
        assert False

    connect_handler(handle_creation, signal=Signals.DOCUMENT_CREATED, sender=dispatcher.Any)
    disconnect_handler(handler=handle_creation, signal=Signals.DOCUMENT_CREATED)
    _ = Document(TEST_DOCUMENT)
    assert True


def test_disconnect_wrong_event():
    def handle_creation(message):
        globals()["cache"]["test_disconnect_wrong_event"] = message

    connect_handler(handle_creation, signal=Signals.DOCUMENT_CREATED, sender=dispatcher.Any)
    disconnect_handler(signal=Signals.DOCUMENT_CLONED)
    _ = Document(TEST_DOCUMENT)
    assert globals()["cache"]["test_disconnect_wrong_event"] is not None


def test_event_document_created():
    def handle_creation(message):
        assert message["type"] == Signals.DOCUMENT_CREATED
        assert type(message["document"]) == Document
        assert message["document"].get_document() == TEST_DOCUMENT

    connect_handler(handle_creation, signal=Signals.DOCUMENT_CREATED, sender=dispatcher.Any)
    _ = Document(TEST_DOCUMENT)
    disconnect_handler(signal=Signals.DOCUMENT_CREATED)


def test_event_document_new_cloned():
    def handle_cloning_new(message):
        assert message["type"] == Signals.DOCUMENT_CLONED
        assert type(message["document"]) == Document
        assert message["document"].get_document() == TEST_DOCUMENT
        assert message["source"].get_document() == TEST_DOCUMENT
        assert message["document"].core_id != message["source"].core_id
        assert message["document"].create_date != message["source"].create_date
        assert message["document"].update_date != message["source"].update_date
        assert message["document"].ttl != message["source"].ttl

    connect_handler(handle_cloning_new, signal=Signals.DOCUMENT_CLONED, sender=dispatcher.Any)
    d = Document(TEST_DOCUMENT, ttl=10)
    d.clone(new=True)
    disconnect_handler(signal=Signals.DOCUMENT_CLONED)


def test_event_document_cloned():
    def handle_cloning(message):
        assert message["type"] == Signals.DOCUMENT_CLONED
        assert type(message["document"]) == Document
        assert message["document"].get_document() == TEST_DOCUMENT
        assert message["source"].get_document() == TEST_DOCUMENT
        assert message["document"].core_id == message["source"].core_id
        assert message["document"].create_date == message["source"].create_date
        assert message["document"].update_date == message["source"].update_date
        assert message["document"].ttl == message["source"].ttl

    connect_handler(handle_cloning, signal=Signals.DOCUMENT_CLONED, sender=dispatcher.Any)
    d = Document(TEST_DOCUMENT)
    d.clone(new=False)
    disconnect_handler(signal=Signals.DOCUMENT_CLONED)


def test_event_document_updated():
    def handle_update(message):
        assert message["type"] == Signals.DOCUMENT_UPDATED
        assert type(message["document"]) == Document
        assert message["document"].get_document() == TEST_DOCUMENT * 2
        assert message["changes"]["from"] == TEST_DOCUMENT
        assert message["changes"]["to"] == TEST_DOCUMENT * 2

    connect_handler(handle_update, signal=Signals.DOCUMENT_UPDATED, sender=dispatcher.Any)
    d = Document(TEST_DOCUMENT)
    d.set_document(TEST_DOCUMENT * 2)
    disconnect_handler(signal=Signals.DOCUMENT_UPDATED)


def test_from_str():
    d = Document(TEST_DOCUMENT)
    dd = Document.from_str(str(d))
    assert str(dd) == str(d)


def test_dict_from_str():
    dico = Document.from_str(dumps(dict(test=Document().toDict())))
    assert type(dico) == dict
    assert type(dico["test"]) == Document


def test_list_from_Str():
    lst = Document.from_str(dumps([Document().toDict(), Document()]))
    assert type(lst) == list
    for d in lst:
        assert type(d) == Document


def test_new_from_str():
    d = Document(TEST_DOCUMENT)
    dd = Document.from_str(str(d), new=True)
    assert str(dd) != str(d)


def test_other_from_str():
    o = Document.from_str(dumps(dict(test="test")))
    assert type(o) == dict
    assert type(o["test"]) == str


def test_repr():
    d = Document()
    r = repr(d)
    assert r == "<class '{c}' - value {v}>".format(c=type(d).__name__, v=dumps(d))


def test_equal():
    d = Document(TEST_DOCUMENT)
    dd = d.clone(new=False)
    assert d == dd


def test_hash():
    d = Document(TEST_DOCUMENT)
    dd = d.clone(new=False)
    assert dd == d
    assert hash(d) == hash(dd)
    assert hash(d) != hash(Document(TEST_DOCUMENT))
    dd.set_document(None)
    assert hash(d) != hash(dd)


def test_child():
    child = Document(TEST_DOCUMENT)
    parent = Document(child)
    children = parent.children()
    assert child in children
    assert len(children) == 1


def test_children():
    parent = Document(Document(TEST_DOCUMENT), Document(TEST_DOCUMENT))
    assert len(parent.children()) == 2

    parent = Document(Document(TEST_DOCUMENT), Document(TEST_DOCUMENT))
    assert len(parent.children()) == 2

    parent = Document(Document(Document(TEST_DOCUMENT)))
    assert len(parent.children()) == 2

    parent = Document(dict(docs=Document(Document(TEST_DOCUMENT))))
    assert len(parent.children()) == 2

    parent = Document([dict(docs=Document(Document(TEST_DOCUMENT))), Document(TEST_DOCUMENT)])
    assert len(parent.children()) == 3

    parent = Document(dict(docs=[Document(Document(TEST_DOCUMENT)), Document(TEST_DOCUMENT)]))
    assert len(parent.children()) == 3

    parent = Document("STRING")
    assert (len(parent.children())) == 0

    parent = Document("STRING", Document("STRING"))
    assert (len(parent.children())) == 1


def test_logger_warn(capture_logs):
    l = create_logger()
    l.warn("WARN")

    assert str(capture_logs) != "No logging captured"


def test_logger_catch_exception(capture_logs):
    l = create_logger()
    with pytest.raises(CoreDocumentException):
        @log_exception(l, exception_type=CoreDocumentException)
        def method():
            raise CoreDocumentException("message")

        method()

        capture_logs.check(
            ('hopla', 'ERROR', 'message'),
        )


def test_logger_does_not_catch_exception(capture_logs):
    l = create_logger()
    with pytest.raises(TypeError):
        @log_exception(l, exception_type=CoreDocumentException)
        def method():
            raise TypeError("message")

        method()

        capture_logs.check(
        )


def test_dispatcher_wrong_handler_type():
    with pytest.raises(Exception) as e_info:
        connect_handler(0, Signals.UNKNOWN)
        assert type(e_info) == TypeError


def test_dispatcher_wrong_signal_type():
    def handler(_):
        pass
    with pytest.raises(Exception) as e_info:
        connect_handler(handler, 0)
        assert type(e_info) == TypeError


def test_dispatcher_wrong_args_count():
    def handler():
        pass

    with pytest.raises(Exception) as e_info:
        connect_handler(handler, Signals.UNKNOWN)
        assert type(e_info) == HandlerArgsCountException


def test_create_schema():
    _ = Schema(value={})
    assert True

    with pytest.raises(ValueError) as e_info:
        _ = Schema()
        assert type(e_info) == ValueError

    with pytest.raises(TypeError) as e_info:
        _ = Schema(value="TEST")
        assert type(e_info) == TypeError


def test_create_options():
    _ = Options()
    assert True

    _ = Options(schema=None)
    assert True

    with pytest.raises(TypeError) as e_info:
        _ = Options(schema="WRONG")
        assert type(e_info) == TypeError


def test_class_properties():
    class Test(Properties):
        @staticmethod
        def from_dict(value):
            pass

    t = Test()

    assert t.data == {}

    t["test"] = "test"
    assert t["test"] == "test"

    del t["test"]
    assert len(t) == 0

    assert list(iter(t)) == []


def test_schema_from_dict():
    v = {}
    s = Schema.from_dict(v)
    assert s.value == v

    v = {"value": {}}
    assert s.value == v["value"]


def test_options_from_dict():
    v =  {"value": {}}
    s = Options.from_dict(v)
    assert s.schema.value == v["value"]
