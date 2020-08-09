"""Helper module for handling azure functions http stuff.

Due to azure functions not having many libraries, this module is quick and dirty
replacement for some authentication and request processing.
"""
import inspect
import json
import logging
import typing

import azure.functions as functions

from . import common as common
from . import users


def _dict_response(response: typing.Union[dict, list], code=200):
    return functions.HttpResponse(
        json.dumps(response), status_code=code, mimetype="application/json"
    )


def response_server_error(message="Server error", code=500) -> functions.HttpResponse:
    """Returns azure http response with server error."""
    return _dict_response({"statusCode": code, "message": message}, code=code)


def dispatcher(get=None, post=None, put=None):
    """Method to simplify handling of GET, POST and so on.

    Usage
    -----
    > dispatch = dispatcher(get=get_handler)
    > return dispatch(request, ....)
    """
    switch = {"GET": get, "POST": post, "PUT": put}

    def _dispatch(req: functions.HttpRequest, *args, **kwargs):
        if not hasattr(req, "method"):
            logging.error("Bad call to method_dispatch. Request object is not first")
            return response_server_error()
        function = switch.get(req.method, None)
        if function:
            return function(req, *args, **kwargs)
        return response_server_error()

    return _dispatch


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
