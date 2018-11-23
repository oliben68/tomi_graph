import warnings
from ujson import dumps
from uuid import uuid4

import pytest
from pydispatch import dispatcher

from hopla.core import DEFAULT_ENCODING
from hopla.documents.document import Document
from hopla.core.events.core_dispatcher import connect_handler
from hopla.core.events.signals import Signals
from hopla.core.exceptions import CoreDocumentException, EncodingWarning, CircularReferenceWarning, \
    SchemaValidationWarning, SchemaValidationException
from hopla.documents.schema_based.document import ValidatedDocument

TEST_VAL = {"document": {"test": "value"}}
TEST_DOCUMENT = "THIS IS A TEST"


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


def test_event_document_created():
    def handle_creation(message):
        assert message["type"] == Signals.DOCUMENT_CREATED
        assert type(message["document"]) == Document
        assert message["document"].get_document() == TEST_DOCUMENT

    connect_handler(handle_creation, signal=Signals.DOCUMENT_CREATED, sender=dispatcher.Any)
    _ = Document(TEST_DOCUMENT)


def test_event_document_new_cloned():
    def handle_cloning(message):
        assert message["type"] == Signals.DOCUMENT_CLONED
        assert type(message["document"]) == Document
        assert message["document"].get_document() == TEST_DOCUMENT
        assert message["source"].get_document() == TEST_DOCUMENT
        assert message["document"].core_id != message["source"].core_id

    connect_handler(handle_cloning, signal=Signals.DOCUMENT_CLONED, sender=dispatcher.Any)
    d = Document(TEST_DOCUMENT)
    d.clone()


def test_event_document_cloned():
    def handle_cloning(message):
        assert message["type"] == Signals.DOCUMENT_CLONED
        assert type(message["document"]) == Document
        assert message["document"].get_document() == TEST_DOCUMENT
        assert message["source"].get_document() == TEST_DOCUMENT
        assert message["document"].core_id == message["source"].core_id

    connect_handler(handle_cloning, signal=Signals.DOCUMENT_CLONED, sender=dispatcher.Any)
    d = Document(TEST_DOCUMENT)
    d.clone(new=False)


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


def test_from_str():
    d = Document(TEST_DOCUMENT)
    dd = Document.from_str(str(d))
    assert str(dd) == str(d)


def test_new_from_str():
    d = Document(TEST_DOCUMENT)
    dd = Document.from_str(str(d), new=True)
    assert str(dd) != str(d)


def test_equal():
    d = Document(TEST_DOCUMENT)
    dd = d.clone(new=False)
    assert d == dd


def test_hash():
    d = Document("A")
    dd = d.clone(new=False)
    assert dd == d
    assert hash(d) == hash(dd)
    assert hash(d) != hash(Document("A"))
