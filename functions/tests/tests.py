"""Endpoint for submitting new tests and viewing results."""
import base64
import json
import logging
import os
import urllib

from ..shared import http, decorators, mongo, users, core, common
from . import validators

import azure.functions as func
from bson import ObjectId
import cerberus
from jose import jws


@decorators.login_required
@decorators.validate_parameters(route_settings=validators.ROUTE_SETTINGS)
def get_test(req, user: users.User, test_id, queue=None):
    user_param = None
    if not user.is_admin:
        user_param = user.email
    result = mongo.MongoTests.get_test(test_id, user=user_param)
    if not result:
        logging.info("Not found result")
        return http.response_not_found()
    return http.response_ok(result)


@decorators.login_required
@decorators.validate_parameters(query_settings=validators.QUERY_SETTINGS)
def list_tests(
    req: func.HttpRequest,
    user: users.User,
    email=None,
    submission_id=None,
    case_id=None,
    task_id=None,
):
    """List all tests, that were run."""
    if not user.is_admin and (not email or email != user.email):
        return http.response_forbidden()
    # If user is really filtering only his submissions, we don't need to
    # validate other parameters (i.e. submission id)
    result = mongo.MongoTests().list_tests(
        email=email, submission_id=submission_id, case_id=case_id, task_id=task_id
    )
    return http.response_ok(list(result))


def get_dispatch(req: func.HttpRequest, queue=None):
    """Dispatch to concrete implementation, based on route."""
    has_id = req.route_params.get("id", None)
    if has_id:
        return get_test(req)  # pylint:disable=no-value-for-parameter
    return list_tests(req)  # pylint:disable=no-value-for-parameter


@decorators.login_required
def post_test(req: func.HttpRequest, user: users.User, queue=None):
    body = http.get_json(req, validators.POST_SCHEMA)
    roles = None
    if not user.is_admin:
        roles = user.roles or []
    if body is None:
        return http.response_client_error()
    if not (self_url := http.get_host_url(req)):
        logging.error("Cannot build host url in post test.")
        return http.response_server_error()
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
        case_name=test_case.name,
        task_id=submission.task_id,
    )
    if not result:
        return http.response_server_error()

    this_test_url = urllib.parse.urljoin(self_url, f'/api/tests/{str(result._id)}')
    notification =  common.encode_message(this_test_url, test_case_id, submission_id)

    queue.set(notification)
    return http.response_ok(result, code=201)

@decorators.validate_parameters(route_settings=validators.ROUTE_SETTINGS)
def patch_handler(request: func.HttpRequest, queue=None, test_id=None) -> func.HttpResponse:
    """Handle update to test result.

    This function will be called by background test machines.  Authentication
    will be done via JOSE, as these machines don't have social network accounts.
    """
    ...
    try:
        if test_id is None:
            return http.response_client_error()
        body = request.get_body()
        secret_key64 = os.environ["QUEUE_SECRET"]
        decoded_key = base64.decodebytes(secret_key64.encode('utf-8'))

        query = json.loads(
            jws.verify(
                body.decode('utf-8'), decoded_key.decode('utf-8'), 'HS256'
                )
            )

        validator = cerberus.Validator(
            validators.PATCH_SCHEMA, allow_unknown=False, require_all=True
        )

        if not validator.validate(query):
            logging.error("Bad json in test update %s", validator.errors)
            return http.response_client_error()
        document = validator.document
        update_result = mongo.MongoTests.update_test(
            test_id,
            document[validators.SCHEMA_TEST_DESCRIPTION],
        )
        if not update_result:
            logging.error("On patch test, update db fail (wrong id?)")
            return http.response_client_error()
        return http.response_ok(None, code=204)
    except Exception as error:
        logging.error("Unknown error in test patch %s", error)
        return http.response_client_error()


def main(req: func.HttpRequest, queue: func.Out[str]) -> func.HttpResponse:  # type: ignore
    """Entry point. Dispatch request based on method."""
    dispatch = http.dispatcher(get=get_dispatch, post=post_test, patch=patch_handler)
    return dispatch(req, queue=queue)
