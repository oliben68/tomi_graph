import warnings
from ujson import dumps
from uuid import uuid4

import pytest
from pydispatch import dispatcher
from testfixtures import LogCapture

from hopla.documents.core import DEFAULT_ENCODING
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

# doc = Document([Document("A"), Document()])
#
# str_doc = str(doc)
#
# ddoc = Document.from_str(str_doc)
#
# ddoc


def test():
    d = Document(TEST_DOCUMENT)
    dd = d.clone(new=False)
    assert d == dd

test()