"""Tetst for our test endpoint."""
import datetime
from unittest.mock import MagicMock

import azure.functions as func
from bson import ObjectId
import pytest

import functions.tests.tests as tests

# import functions.shared.mongo
from functions.shared import mongo, users, models


def mock_test_case():
    return models.TestCase(
        _id=ObjectId,
        task_id=ObjectId(),
        name="",
        runs_allowed=2,
        roles=["student2020"],
        does_count=True,
    )


def mock_submission():
    return models.Submission(
        _id=ObjectId, task_id=ObjectId(), date=datetime.datetime.now(), user="a"
    )


def mock_test_run():
    return models.TestRun(
        _id=ObjectId(),
        submission_id=ObjectId(),
        case_id=ObjectId(),
        description="abcd",
        requested=datetime.datetime.now(),
    )


EMAIL1 = "miro@example.com"


def create_get_request(route=None, params=None, body=None):
    headers = {"X-REQUEST-EMAIL": EMAIL1}
    if body is None:
        body = "{}"
    return func.HttpRequest(
        "GET", "http://localhost:3000", headers=headers, body=body, route_params=route
    )


def create_post_request(body=None):
    headers = {"X-REQUEST-EMAIL": EMAIL1}
    if body is None:
        body = "{}"
    return func.HttpRequest("POST", "http://localhost:3000", headers=headers, body=body)


@pytest.fixture(autouse=True)
def patch_users(monkeypatch):
    mock = MagicMock()
    mock.get_user.return_value = users.User(email=EMAIL1)
    mock.get_case.return_value = mock_test_case()
    mock.create_test.return_value = mock_test_run()
    mock.get_submission.return_value = mock_submission()
    mock.count_tests.return_value = 1
    monkeypatch.setattr(mongo, "MongoUsers", mock)
    monkeypatch.setattr(mongo, "MongoTests", mock)
    monkeypatch.setattr(mongo, "MongoSubmissions", mock)
    monkeypatch.setattr(mongo, "MongoTestCases", mock)



def test_list_all_not_admin():
    ret = tests.main(create_get_request(), MagicMock())
    assert ret.status_code == 403


def test_show_test():
    ret = tests.main(
        create_get_request(route={"id": "5f3944f1bf1bb81e48bae8fa"}), MagicMock()
    )
    assert ret.status_code == 200


def test_post_bad_schema():
    body = """
    {
        "testCaseId" : "5f3e8f187e296d1539d94845",
        "submissionId" : "5f3fe66c754fe8c28fe75239",
        "somethingElse" 1
    }
    """
    ret = tests.main(create_post_request(body=body), MagicMock())
    assert ret.status_code == 400


POST_BODY = """
    {
        "testCaseId" : "5f3e8f187e296d1539d94845",
        "submissionId" : "5f3fe66c754fe8c28fe75239"
    }
    """.encode(
    "utf-8"
)


class TestPost:
    """Test post method of test endpoint."""

    def test_post_too_many_tests(self, monkeypatch):
        """Test what happens on too many test already run."""
        mock = MagicMock()
        mock.return_value = 4
        monkeypatch.setattr(mongo.MongoTests, "count_tests", mock)
        ret = tests.main(create_post_request(body=POST_BODY), MagicMock())
        assert ret.status_code == 402  # Payment required :)

    def test_testcase_ne(self, monkeypatch):
        """Test what if test case doesn't exists."""
        mock = MagicMock()
        mock.get_case.return_value = None
        monkeypatch.setattr(mongo, "MongoTestCases", mock)
        ret = tests.main(create_post_request(body=POST_BODY), MagicMock())
        assert ret.status_code == 404

    def test_all_good(self, monkeypatch):
        ret = tests.main(create_post_request(body=POST_BODY), MagicMock())
        assert ret.status_code == 201
