import logging
import inspect
from .http import response_server_error
from . import common as common
import typing
import azure.functions as functions
from . import users

def login_required(func: typing.Callable):
    """Decorator handling users.

    If your function uses 'user' as keyword parameter, it will be filled with
    current user instance.
    """
    set_user = False
    user_in_args = "user"  # Keyword arg that gets filled
    if user_in_args in inspect.signature(func).parameters:
        set_user = True  # Wrapped function does have 'user' keyword

    def _user_wrapper(req: functions.HttpRequest, *args, **kwargs):
        email = req.headers.get(common.HEADER_EMAIL, "")
        if not users.validate_email(email):
            logging.warning(
                "Rejecting not an email %s in %s field", email, common.HEADER_EMAIL
            )
            return response_server_error()
        # User is authenticated, now get his details, if function is interested
        # in them
        keyword_args = {}
        if set_user:
            user = users.get_user(email)
            keyword_args[user_in_args] = user
        return func(req, *args, **keyword_args)

    return _user_wrapper
