from ..shared import http, decorators, mongo, users

import azure.functions as func

@decorators.login_required
def get_list(req: func.HttpRequest, user: users.User):
    """Get list of all users.

    This is for admins only.
    """
    if not user.is_admin:
        return http.response_forbidden()
    all_users = mongo.MongoUsers.get_users()
    return http.response_ok(list(all_users))

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Dispatch request to correct function."""
    dispatcher = http.dispatcher(get=get_list)
    return dispatcher(req)
