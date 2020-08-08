"""Helper module for handling azure functions http stuff.

Due to azure functions not having many libraries, this module is quick and dirty
replacement for some authentication and request processing.
"""
import logging
import json
import typing

import azure.functions as functions

def _dict_response(response: typing.Union[dict, list], code=200):
    return functions.HttpResponse(
        json.dumps(response), status_code=code, mimetype="application/json"
    )

def response_server_error(message="Server error", code=500) -> functions.HttpResponse:
    """Returns azure http response with server error."""
    return _dict_response({"error": message, "statusCode": code}, code=code)


def dispatcher(get=None, post=None, put=None):
    """Method to simplify handling of GET, POST and so on.

    Usage
    -----
    > dispatch = dispatcher(get=get_handler)
    > return dispatch(request, ....)
    """
    switch = {
        "GET": get,
        "POST": post,
        "PUT": put
    }

    def _dispatch(req: functions.HttpRequest, *args, **kwargs):
        if not hasattr(req, "method"):
            logging.error("Bad call to method_dispatch. Request object is not first")
            return response_server_error()
        function = switch.get(req.method, None)
        if function:
            return function(req, *args, **kwargs)
        return response_server_error()
    return _dispatch
