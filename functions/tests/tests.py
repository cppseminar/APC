"""Endpoint for submitting new tests and viewing results."""
import logging

from ..shared import http, decorators, mongo, users
from . import validators

import azure.functions as func
from bson import ObjectId


@decorators.login_required
@decorators.validate_parameters(route_settings=validators.ROUTE_SETTINGS)
def get_test(req, user, test_id):
    return http.response_ok({})


def get_dispatch(req: func.HttpRequest):
    """Dispatch to concrete implementation, based on route."""
    has_id = req.route_params.get("id", None)
    if has_id:
        return get_test(req)  # pylint:disable=no-value-for-parameter
    return http.response_forbidden()


@decorators.login_required
def post_test(req: func.HttpRequest, user: users.User):
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
    if test_case.does_count:
        ...
        # We have to count nubmer of runs
    # Select submission

    # Count already run tests - but only maybe

    # Submit new one
    return http.response_server_error()


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Entry point. Dispatch request based on method."""
    dispatch = http.dispatcher(get=get_dispatch, post=post_test)
    return dispatch(req)
