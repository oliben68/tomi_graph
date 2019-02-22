import warnings
from ujson import dumps
from uuid import uuid4

import pytest
from testfixtures import LogCapture

from hopla.base.graphs.nodes.core import DEFAULT_ENCODING
from hopla.base.graphs.nodes.node import Node
from hopla.base.graphs.nodes.exceptions import CoreDocumentException, EncodingWarning, CircularReferenceWarning
from hopla.base.shared.logging import create_logger
from hopla.base.shared.logging.auto.logging import auto_log

globals()["cache"] = {}

TEST_VAL = {"data": {"test": "value"}}
TEST_DATA = "THIS IS A TEST"


@pytest.fixture(autouse=True)
def capture_logs():
    with LogCapture() as capture:
        yield capture


def test_init():
    doc = Node()
    assert doc.get_data() is None
    assert doc.core_id is not None
    assert type(doc.core_id) == str
    assert doc.key is None
    assert doc.encoding == "utf-8"

    core_id = str(uuid4())
    key = "this is a key"
    doc = Node(core_id=core_id, key=key, data=TEST_VAL)
    assert doc.core_id == core_id
    assert doc.key == key
    assert doc.get_data() == TEST_VAL

    doc = Node(data=TEST_DATA)
    assert doc.get_data() == TEST_DATA

    encoding = DEFAULT_ENCODING
    bytes_val = TEST_DATA.encode(encoding)
    doc = Node(data=TEST_DATA)
    assert doc.get_data() == bytes_val.decode(encoding)

    encoding = "utf-16"
    bytes_val = TEST_DATA.encode(encoding)
    doc = Node(data=bytes_val, encoding=encoding)
    assert doc.get_data() == bytes_val.decode(encoding)


def test_name_is_string():
    with pytest.raises(Exception) as e_info:
        Node(name=123)
        assert type(e_info) == CoreDocumentException
    Node(name="name")
    assert True


def test_ttl_is_numeric():
    with pytest.raises(Exception) as e_info:
        Node(ttl="NOPE")
        assert type(e_info) == CoreDocumentException
    Node(ttl=0)
    Node(ttl="0")
    Node(ttl="0.123")
    Node(ttl=.123)


def test_encoding_warning(recwarn):
    encoding = "utf-16"
    bytes_val = dumps(TEST_VAL).encode(encoding)
    warnings.simplefilter("always")
    doc = Node(data=bytes_val)
    assert len(recwarn) == 1
    assert recwarn.pop(EncodingWarning)
    assert doc.encoding.lower() == encoding


def test_circular_warning(recwarn):
    warnings.simplefilter("always")
    inner_doc = Node()
    main_doc = Node(data=inner_doc)
    inner_doc.set_data(main_doc)
    assert len(recwarn) == 1
    assert recwarn.pop(CircularReferenceWarning)


def test_init_with_serialize_exc():
    val = dumps({"test": "value"})
    with pytest.raises(Exception) as e_info:
        Node(data=val[0:len(val) - 2])
        assert type(e_info) == CoreDocumentException
        assert "Unexpected character" in str(e_info)


def test_init_stream(tmpdir):
    str_value = dumps(TEST_VAL)
    val = tmpdir.mkdir("sub").join("value.json")
    val.write(str_value)
    doc = Node(data=val)
    assert doc.get_data() == TEST_VAL


def test_init_stream_with_exc(tmpdir):
    str_value = dumps(TEST_VAL)
    val = tmpdir.mkdir("sub").join("value.json")
    val.write(str_value[0:len(str_value) - 2])
    with pytest.raises(Exception) as e_info:
        Node(data=val)
        assert type(e_info) == CoreDocumentException


def test_from_str():
    d = Node(TEST_DATA)
    dd = Node.from_str(str(d))
    assert str(dd) == str(d)


def test_dict_from_str():
    dico = Node.from_str(dumps(dict(test=Node().toDict())))
    assert type(dico) == dict
    assert type(dico["test"]) == Node


def test_list_from_str():
    lst = Node.from_str(dumps([Node().toDict(), Node()]))
    assert type(lst) == list
    for d in lst:
        assert type(d) == Node


def test_new_from_str():
    d = Node(TEST_DATA)
    dd = Node.from_str(str(d), new=True)
    assert str(dd) != str(d)


def test_other_from_str():
    o = Node.from_str(dumps(dict(test="test")))
    assert type(o) == dict
    assert type(o["test"]) == str


def test_repr():
    d = Node()
    r = repr(d)
    assert r == "<type '{c}' - value {v}>".format(c=type(d).__name__, v=dumps(d))


def test_equal():
    d = Node(TEST_DATA)
    dd = d.clone(new=False)
    assert d == dd


def test_hash():
    d = Node(TEST_DATA)
    dd = d.clone(new=False)
    assert dd == d
    assert hash(d) == hash(dd)
    assert hash(d) != hash(Node(TEST_DATA))
    dd.set_data(None)
    assert hash(d) != hash(dd)


def test_child():
    child = Node(TEST_DATA)
    parent = Node(child)
    children = parent.children()
    assert child in children
    assert len(children) == 1


def test_children():
    parent = Node(Node(TEST_DATA), Node(TEST_DATA))
    assert len(parent.children()) == 2

    parent = Node(Node(TEST_DATA), Node(TEST_DATA))
    assert len(parent.children()) == 2

    parent = Node(Node(Node(TEST_DATA)))
    assert len(parent.children()) == 2

    parent = Node(dict(docs=Node(Node(TEST_DATA))))
    assert len(parent.children()) == 2

    parent = Node([dict(docs=Node(Node(TEST_DATA))), Node(TEST_DATA)])
    assert len(parent.children()) == 3

    parent = Node(dict(docs=[Node(Node(TEST_DATA)), Node(TEST_DATA)]))
    assert len(parent.children()) == 3

    parent = Node("STRING")
    assert (len(parent.children())) == 0

    parent = Node("STRING", Node("STRING"))
    assert (len(parent.children())) == 1


def test_logger_warn(capture_logs):
    l = create_logger()
    l.warn("WARN")

    assert str(capture_logs) != "No logging captured"


def test_logger_catch_exception(capture_logs):
    l = create_logger()
    with pytest.raises(CoreDocumentException):
        @auto_log(l, exception_type=CoreDocumentException)
        def method():
            raise CoreDocumentException("message")

        method()

        capture_logs.check(
            ('hopla.', 'ERROR', 'message'),
        )


def test_logger_catch_exception_defautls(capture_logs):
    with pytest.raises(CoreDocumentException):
        @auto_log(exception_type=CoreDocumentException)
        def method():
            raise CoreDocumentException("message")

        method()

        capture_logs.check(
            ('hopla.', 'ERROR', 'message'),
        )


def test_logger_does_not_catch_exception(capture_logs):
    l = create_logger()
    with pytest.raises(TypeError):
        @auto_log(l, exception_type=CoreDocumentException)
        def method():
            raise TypeError("message")

        method()

        capture_logs.check(
        )


def test_dispatcher_wrong_args_count():
    def handler():
        pass
