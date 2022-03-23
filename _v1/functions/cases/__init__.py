"""Endpoint for retrieving test cases description."""
import typing

import azure.functions as func
from bson import ObjectId

from ..shared import http, decorators, users, mongo

ROUTE_SETTINGS = {
    "id": {
        decorators.VALIDATOR: decorators.object_id_validator,
        decorators.DESTINATION: "case_id",
    }
}

QUERY_SETTINGS = {
    "task": {
        decorators.VALIDATOR: decorators.object_id_validator,
        decorators.DESTINATION: "task_id",
    }
}


@decorators.login_required
@decorators.validate_parameters(route_settings=ROUTE_SETTINGS)
def get_case(_: func.HttpRequest, user: users.User, case_id):
    """Return single case from db, if you have right access."""
    roles = None
    if not user.is_admin:
        roles = user.roles or []
    result = mongo.MongoTestCases.get_case(ObjectId(case_id), roles)
    if not result:
        return http.response_not_found()
    return http.response_ok(result)


@decorators.login_required
@decorators.validate_parameters(query_settings=QUERY_SETTINGS)
def get_cases(_: func.HttpRequest, user: users.User, task_id: str = None):
    """List all cases for given task id."""
    roles: typing.Optional[typing.List] = user.roles
    if user.is_admin:
        roles = None
    if task_id:
        task_id = ObjectId(task_id)
    result = mongo.MongoTestCases.get_cases(task_id=task_id, roles=roles)
    return http.response_ok(list(result))


def get_handler(req: func.HttpRequest):
    """Peek on route and decide which function to call."""
    has_id = req.route_params.get("id", None)
    if has_id:
        return get_case(req)  # pylint:disable=no-value-for-parameter
    return get_cases(req)  # pylint:disable=no-value-for-parameter


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Send Get method to get handler."""
    dispatch = http.dispatcher(get=get_handler)
    return dispatch(req)
