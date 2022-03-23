"""Endpoint for getting and listing tasks."""
import azure.functions as func

from ..shared import http, decorators, mongo, users, core


ROUTE_PARAMS = {
    "id": {
        decorators.VALIDATOR: decorators.object_id_validator,
        decorators.DESTINATION: "submission_id",
    }
}


def _user_validator(value):
    if core.is_email(value):
        return str(value)
    raise ValueError(f"Not an email {value}")


QUERY_PARAMS = {
    "user": {
        decorators.VALIDATOR: _user_validator,
        decorators.DESTINATION: "user_filter",
    }
}


@decorators.validate_parameters(
    route_settings=ROUTE_PARAMS, query_settings=QUERY_PARAMS
)
@decorators.login_required
def get_handler(req, user: users.User, submission_id=None, user_filter=None):
    """Handler for HTTP GET."""
    if submission_id:
        # User wants to see concrete task
        roles = None if user.is_admin else user.roles
        return get_task(submission_id, roles)

    roles = user.roles

    if not user.is_admin and (not user_filter or user_filter != user.email):
        # Only admin can query all
        return http.response_forbidden()

    if user.is_admin and not user_filter:
        roles = None
    elif user.is_admin:  # Admin is impersonating someone
        roles = mongo.MongoUsers().get_user(user_filter).roles  # upsert

    result = mongo.MongoTasks.get_tasks(roles=roles)
    return http.response_ok(list(result))


def get_task(task_id: str, roles):
    """Get concrete task, based on task id.

    If roles doesn't match those of task, return 404
    """
    result = mongo.MongoTasks.get_task(task_id, roles=roles)
    if not result:
        return http.response_not_found()
    return http.response_ok(result)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Entry point."""
    return http.dispatcher(get=get_handler)(req)
