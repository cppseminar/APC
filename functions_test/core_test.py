import dataclasses
import datetime
import json
import pytest

from bson import ObjectId
from functions.shared.core import is_email, MongoEncoder, instantiate_dataclass

def test_validate_email():
    """Test our simple validator."""
    assert is_email("abcd") == False
    assert is_email("abcd@ef.gh") == True
    assert is_email("ab cd@gmail.com") == False
    assert is_email("abee[at]gmail.com") == False
    assert is_email("abee@gmail.party") == True
    assert is_email("abee.tyler@gmail.party") == True
    assert is_email("jozko.marek23@fmfi.uniba.sk")


class TestMongoEncoder:
    """Tests for our custom handling of mongo objects."""

    def test_datetime(self):
        document = {"date": datetime.datetime(2012, 12, 21, 1, 0, 0)}
        result = json.dumps(document, cls=MongoEncoder)
        assert result == r'{"date": "2012-12-21T01:00:00+00:00"}'

    def test_object_id(self):
        document = {"_id": ObjectId("5f3172e94ccb2b29ecbf28e0")}
        result = json.dumps(document, cls=MongoEncoder)
        assert result == """{"_id": "5f3172e94ccb2b29ecbf28e0"}"""


class TestDataclassInstantiate:
    """Few tests for dataclass instantiation."""

    def test_standard_class(self):
        class Ghj:
            pass
        with pytest.raises(TypeError):
            instantiate_dataclass(Ghj, abcd=1)

    def test_instantiate_normal(self):
        @dataclasses.dataclass
        class Dtc:
            req_id: int
            some_id: int = 1234

        result = instantiate_dataclass(Dtc, req_id=1)
        assert result.req_id == 1
        assert result.some_id == 1234

    def test_instantiate_more(self):
        @dataclasses.dataclass
        class Dtc:
            req_id: str
            some_id: int = 1234

        result = instantiate_dataclass(Dtc, req_id="aa", ne_column=2, some_id=1)
        assert result.req_id == "aa"
        assert result.some_id == 1

