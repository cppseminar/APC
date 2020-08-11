"""Helper module for handling azure functions http stuff.

Due to azure functions not having many libraries, this module is quick and dirty
replacement for some authentication and request processing.
"""
import json
import contextlib
import logging
import typing

import azure.functions as functions
import bson.json_util


def response_ok(document: typing.Any, code=200):
    """Return response. Only accepts json serializable."""
    response_str = ""
    try:
        # Try converting to json
        with contextlib.suppress(TypeError):
            response_str = json.dumps(document)
        if not response_str:
            # Let's try bson now
            response_str = bson.json_util.dumps(
                document, json_options=bson.json_util.RELAXED_JSON_OPTIONS
            )
    except (Exception) as error: # pylint: disable=W0703
        logging.error("Serialization went wrong %s", error)
        return response_server_error()

    return functions.HttpResponse(
        response_str, status_code=code, mimetype="application/json"
    )


def _dict_response(response: typing.Union[dict, list], code=200):
    return functions.HttpResponse(
        json.dumps(response), status_code=code, mimetype="application/json"
    )


def response_server_error(message="Server error", code=500) -> functions.HttpResponse:
    """Returns azure http response with server error."""
    return _dict_response({"statusCode": code, "message": message}, code=code)


def response_client_error(message="Error bad request",
                          code=400) -> functions.HttpResponse:
    """Returns azure http response filled with bad request code and message."""
    return _dict_response({"statusCode": code, "message": message}, code=code)


def response_not_found():
    """Return standard 404 not found."""
    return response_client_error(message="Object not found", code=404)


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
