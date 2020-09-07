"""Endpoint for submitting new tests and viewing results."""
import json
import logging

from ..shared import http, decorators, mongo, users, core
from . import validators

import azure.functions as func
from bson import ObjectId


@decorators.login_required
@decorators.validate_parameters(route_settings=validators.ROUTE_SETTINGS)
def get_test(req, user, test_id, queue=None):
    return http.response_ok({})


def get_dispatch(req: func.HttpRequest, queue=None):
    """Dispatch to concrete implementation, based on route."""
    has_id = req.route_params.get("id", None)
    if has_id:
        return get_test(req)  # pylint:disable=no-value-for-parameter
    return http.response_forbidden()


@decorators.login_required
def post_test(req: func.HttpRequest, user: users.User, queue=None):
    body = http.get_json(req, validators.POST_SCHEMA)
    roles = None
    if not user.is_admin:
        roles = user.roles or []
    if body is None:
        return http.response_client_error()
    # First let's check if test case exists
    test_case_id = ObjectId(body[validators.SCHEMA_CASE_ID])
    test_case = mongo.MongoTestCases.get_case(case_id=test_case_id, roles=roles)
    if test_case is None:
        return http.response_not_found()
    # Test case was found, so user has right to execute it. We are not going
    # to check, if this test case is for this concrete submission. We don't care
    if test_case.does_count and not user.is_admin:
        count = mongo.MongoTests.count_tests(case_id=test_case_id, user=user.email)
        if count >= test_case.runs_allowed:
            return http.response_payment()

    # This run is allowed, either it does not count, or we counted number of
    # runs, and incresed number on submissions. This is bascially race on
    # parallel requests, but even if successfully exploited, gains are like
    # one more test run, so who cares.
    submission_id = ObjectId(body[validators.SCHEMA_SUBMISSION_ID])
    user_param = None
    if not user.is_admin:
        user_param = user.email
    submission = mongo.MongoSubmissions.get_submission(
        submission_id=submission_id, user=user_param
    )
    if not submission:
        return http.response_not_found()

    if user.email == submission.user:  # Let's mark submission as test run
        mongo.MongoSubmissions.increment_test(submission_id)

    result = mongo.MongoTests.create_test(
        user=user.email,
        submission_id=submission_id,
        case_id=test_case_id,
        task_name=submission.task_name,
    )
    if not result:
        return http.response_server_error()

    notification = json.dumps(dict(result), cls=core.MongoEncoder, indent=2)
    queue.set(notification)
    return http.response_ok(result, code=201)


def main(req: func.HttpRequest, queue: func.Out[str]) -> func.HttpResponse:  # type: ignore
    """Entry point. Dispatch request based on method."""
    dispatch = http.dispatcher(get=get_dispatch, post=post_test)
    return dispatch(req, queue=queue)
