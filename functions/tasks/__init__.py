import azure.functions as func

from ..shared import http, decorators, mongo


ROUTE_PARAMS = {
    "id": {
        decorators.VALIDATOR: decorators.object_id_validator,
        decorators.DESTINATION: "submission_id",
    }
}

@decorators.validate_parameters(route_settings=ROUTE_PARAMS)
@decorators.login_required
def get_handler(req, user, submission_id=None):
    if not submission_id:
        result = mongo.MongoTasks.get_tasks()
        return http.response_ok(list(result))
    # TODO: Lots of validation
    result = mongo.MongoTasks.get_task(submission_id)
    if not result:
        return http.response_not_found()
    return http.response_ok(result)

def main(req: func.HttpRequest) -> func.HttpResponse:
    return http.dispatcher(get=get_handler)(req)
