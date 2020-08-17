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

@decorators.validate_parameters(route_settings=ROUTE_PARAMS, query_settings=QUERY_PARAMS)
@decorators.login_required
def get_handler(req, user: users.User, submission_id=None, user_filter=None):
    if user_filter and user_filter != user.email:
        # We suppport query only for our own email
        return http.response_forbidden()
    if not user_filter and not user.is_admin:
        # Only admin can query all
        return http.response_forbidden()
    roles = None
    if user_filter:
        roles = user.roles
    # AUTH is done

    # Get all tasks
    if not submission_id:
        result = mongo.MongoTasks.get_tasks(roles=roles)
        return http.response_ok(list(result))
    # Get concrete task
    result = mongo.MongoTasks.get_task(submission_id, roles=roles)
    if not result:
        return http.response_not_found()
    return http.response_ok(result)

def main(req: func.HttpRequest) -> func.HttpResponse:
    return http.dispatcher(get=get_handler)(req)
