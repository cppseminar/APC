import dataclasses
import datetime
import json
import pytest

from bson import ObjectId
from functions.shared.core import (
    is_email,
    MongoEncoder,
    ModelBase,
    instantiate_dataclass,
    empty_dataclass_dict,
    mongo_filter_errors
)


def test_validate_email():
    """Test our simple validator."""
    assert is_email("abcd") == False
    assert is_email("abcd@ef.gh") == True
    assert is_email("ab cd@gmail.com") == False
    assert is_email("abee[at]gmail.com") == False
    assert is_email("abee@gmail.party") == True
    assert is_email("abee.tyler@gmail.party") == True
    assert is_email("jozko.marek23@fmfi.uniba.sk") == True


class TestModelBase:

    def test_map_item(self):

        @dataclasses.dataclass
        class Cls(ModelBase):
            def map_item(self, item):
                key, value = item
                if key == '_id':
                    key = 'Id'
                return key, value

        datac = Cls(_id=ObjectId("5f3172e94ccb2b29ecbf28e0"))
        result = dict(datac)
        assert result == {"Id":ObjectId("5f3172e94ccb2b29ecbf28e0")}

    def test_filter_item(self):

        @dataclasses.dataclass
        class Cls(ModelBase):
            id2: int = 1
            id3: int = 4

            def filter_item(self, item):
                key, value = item
                if key == 'id3':
                    return True
                return False

        datac = Cls(_id=ObjectId("5f3172e94ccb2b29ecbf28e0"))
        result = dict(datac)
        assert result == {"id3": 4}



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

    def test_model_base(self):
        @dataclasses.dataclass
        class Cls(ModelBase):
            id2: int = 1
        string_id = "5f4394ec5e854afcff62fe49"
        datac = Cls(_id=ObjectId("5f4394ec5e854afcff62fe49"))
        result = json.dumps(datac, cls=MongoEncoder)
        print(result)
        assert result == '{"_id": "%s", "id2": 1}' % string_id


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


class TestEmptyDataclassDict:
    def test_defaults(self):
        @dataclasses.dataclass
        class Dtc:
            some_str: str = dataclasses.field(default_factory=str)
            some_id: int = 1234

        result = empty_dataclass_dict(Dtc)
        assert result["some_str"] == ""
        assert result["some_id"] == 1234

    def test_required(self):
        @dataclasses.dataclass
        class Dtc:
            obj_id: ObjectId
        result = empty_dataclass_dict(Dtc)
        assert ObjectId.is_valid(result["obj_id"])

    def test_custom(self):
        class _NotSimple:
            def __init__(self, some_arg):
                raise RuntimeError("Bad init")

        @dataclasses.dataclass
        class Dtc:
            obj: _NotSimple

        result = empty_dataclass_dict(Dtc)
        assert result["obj"] == ""


class TestMongoFilterErrors:

    def test_single_object(self):

        def _throws(obj):
            raise RuntimeError("Abcde")

        def _returns(obj):
            return 5

        assert mongo_filter_errors(ObjectId(), _throws) is None
        assert mongo_filter_errors(ObjectId(), _returns) == 5

    def test_mulitple(self):

        def _func(obj):
            if obj == 5:
                raise RuntimeError("Idk")
            return obj
        input_list = [1, 5, 3]
        result = mongo_filter_errors(input_list, _func)
        assert list(result) == [1, 3]

