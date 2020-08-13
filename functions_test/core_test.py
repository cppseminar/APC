import datetime
import json
import pytest

from bson import ObjectId
from functions.shared.core import is_email, MongoEncoder

def test_validate_email():
    """Test our simple validator."""
    assert is_email("abcd") == False
    assert is_email("abcd@ef.gh") == True
    assert is_email("ab cd@gmail.com") == False
    assert is_email("abee[at]gmail.com") == False
    assert is_email("abee@gmail.party") == True


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


