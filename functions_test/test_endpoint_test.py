"""Tetst for our test endpoint."""
from unittest.mock import MagicMock

import azure.functions as func

import functions.tests.tests as tests
# import functions.shared.mongo
from functions.shared import mongo, users
import pytest

EMAIL1 = 'miro@example.com'

def create_get_request(route=None, params=None, body=None):
    headers = {"X-REQUEST-EMAIL": EMAIL1}
    if body is None:
        body = "{}"
    return func.HttpRequest("GET", "http://localhost:3000",
                                 headers=headers, body=body,
                                 route_params=route)


def create_post_request(body=None):
    headers = {"X-REQUEST-EMAIL": EMAIL1}
    if body is None:
        body = "{}"
    return func.HttpRequest("POST", "http://localhost:3000",
                                 headers=headers, body=body)

@pytest.fixture(autouse=True)
def patch_users(monkeypatch):
    mock = MagicMock()
    mock.get_user.return_value = users.User(email=EMAIL1)
    monkeypatch.setattr(mongo, "MongoUsers", mock)



def test_list_all_not_admin():
    ret = tests.main(create_get_request())
    assert ret.status_code == 403
    

def test_show_test():
    ret = tests.main(create_get_request(route={"id": "5f3944f1bf1bb81e48bae8fa"}))
    assert ret.status_code == 200


def test_post_bad_schema():
    body = """
    {
        "tesCaseId" : "5f3e8f187e296d1539d94845",
        "submissionId" : "5f3fe66c754fe8c28fe75239",
        "somethingElse" 1
    }
    """
    ret = tests.main(create_post_request(body=body))
    assert ret.status_code == 400

def test_post_too_many_tests():
    body = """
    {
        "tesCaseId" : "5f3e8f187e296d1539d94845",
        "submissionId" : "5f3fe66c754fe8c28fe75239",
    }
    """
    ret = tests.main(create_post_request(body=body))
    



