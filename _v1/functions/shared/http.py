"""Helper module for handling azure functions http stuff.

Due to azure functions not having many libraries, this module is quick and dirty
replacement for some authentication and request processing.
"""
import json
import contextlib
import logging
import os
import typing
import urllib

import azure.functions as functions
import bson.json_util
import cerberus

from . import core, common


def response_ok(document: typing.Any, code=200):
    """Return response. Only accepts json serializable."""
    response_str = ""
    if code == 204: # Handle no content
        return functions.HttpResponse(status_code=code)
    # Let's try returning json
    try:
        # Try converting to json
        with contextlib.suppress(TypeError):
            response_str = json.dumps(
                document,
                skipkeys=False,
                allow_nan=False,
                indent=2,
                cls=core.MongoEncoder,
            )
        if not response_str:
            # Let's try bson now
            response_str = bson.json_util.dumps(
                document, json_options=bson.json_util.RELAXED_JSON_OPTIONS
            )
    except (Exception) as error:  # pylint: disable=W0703
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


def response_client_error(
    message="Error bad request", code=400
) -> functions.HttpResponse:
    """Returns azure http response filled with bad request code and message."""
    return _dict_response({"statusCode": code, "message": message}, code=code)


def response_not_found():
    """Return standard 404 not found."""
    return response_client_error(message="Object not found", code=404)

def response_forbidden():
    """Return 403."""
    return response_client_error(message="This action is forbidden", code=403)

def response_payment():
    """Return 402."""
    return response_client_error(message="Payment Required", code=402)

def dispatcher(get=None, post=None, put=None, patch=None):
    """Method to simplify handling of GET, POST and so on.

    Usage
    -----
    > dispatch = dispatcher(get=get_handler)
    > return dispatch(request, arg2, kwarg1, ...)
    """
    switch = {"GET": get, "POST": post, "PUT": put, "PATCH": patch}

    def _dispatch(req: functions.HttpRequest, *args, **kwargs):
        if not hasattr(req, "method"):
            logging.error("Bad call to method_dispatch. Request object is not first")
            return response_server_error()
        function = switch.get(req.method, None)
        if function:
            return function(req, *args, **kwargs)
        return response_server_error()

    return _dispatch


def get_json(request: functions.HttpRequest, schema: dict, /):
    """Validate submitted json schema. Returns dict or None."""
    try:
        data = request.get_json()
        validator = cerberus.Validator(schema, allow_unknown=False, require_all=True)
        if not validator.validate(data):
            logging.warning("Error in json %s", validator.errors)
            return None
        return validator.document
    except TypeError:
        logging.warn("Received non json request")
    except Exception as error:
        logging.error("Error in handling json %s", error)
    return None

def get_host_url(request: functions.HttpRequest):
    """Tries to build url from request.

    At first, tries to build it from x-forwarded headers. On failure reverts
    to request url. If this fails too, returns empty string.
    """
    _debug = os.environ.get(common.ENV_HOST_OVERRIDE, None)
    if _debug: # This is not nice, but at least we have unit tests
        return _debug
    host = request.headers.get(common.HTTP_HEADER_HOST, None)
    protocol = request.headers.get(common.HTTP_HEADER_PROTOCOL, "https")
    if (port := request.headers.get(common.HTTP_HEADER_PORT, None)) and host:
        host = host.split(":")[0] +  f":{port}"

    if not host:
        _parts = urllib.parse.urlparse(request.url)
        protocol, host = _parts[0], _parts[1]

    parts = [protocol, host] + [""] * 4
    return urllib.parse.urlunparse(tuple(parts))
